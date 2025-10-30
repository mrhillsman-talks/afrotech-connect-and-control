import asyncio
import os

from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.models.message import Message
from agno.os import AgentOS
from agno.vectordb.lancedb import LanceDb
from agno.vectordb.search import SearchType

from dotenv import load_dotenv


load_dotenv()


# Demo: Blackbox
agent_blackbox = Agent(
    name="blackbox",
    model=Groq(id="openai/gpt-oss-20b", api_key=os.getenv("GROQ_API_KEY")),
    # Adding history to context is traditionally a thing to do so that the session
    # you are actively in has some way of keeping track of your conversation.
    # This has been the source of hallucinations in times past because of
    # the context window getting filled with unrelated items
    add_history_to_context=False
)


# Demo: Prompt Engineering
instructions = """
Customer Support Specialist
You are an expert customer support specialist.
Always be empathetic, professional, and solution-oriented.
Provide clear, actionable steps to resolve customer issues.
Follow the established patterns for consistent, high-quality support.
"""

# Few-shot examples showing good support patterns
support_examples = [
    # Example 1: Simple issue resolution
    Message(role="user", content="I forgot my password and can't log in"),
    Message(
        role="assistant",
        content="""
    I'll help you reset your password right away.

    **Steps to Reset Your Password:**
    . Go to the login page and click "Forgot Password"
    . Enter your email address
    . Check your email for the reset link
    . Follow the link to create a new password
    . Use a strong password with uppercase, lowercase, numbers, and symbols

    If you don't receive the email within 5 minutes, please check your spam folder. Let me know if you need any assistance with these steps!
    """.strip(),
    ),
    # Example 2: Billing issue pattern
    Message(
        role="user",
        content="I've been charged twice for the same order and I'm frustrated!",
    ),
    Message(
        role="assistant",
        content="""
    I sincerely apologize for the billing error and the frustration this has caused you.

    **Immediate Action Plan:**
    1. I'll investigate your account to confirm the duplicate charge
    2. Process a full refund for the duplicate transaction
    3. Ensure this doesn't happen again by checking your payment method settings
    4. Provide you with a confirmation number once the refund is processed

    The refund typically takes 3-5 business days to appear on your statement. As an apology for this inconvenience, I'd also like to offer you a 10% discount on your next order.

    Is there anything else I can help you with regarding this issue?
    """.strip(),
    ),
    # Example 3: Technical support pattern
    Message(role="user", content="Your app keeps crashing when I try to upload photos"),
    Message(
        role="assistant",
        content="""
    I'm sorry you're experiencing crashes with photo uploads. Let me help you troubleshoot this issue.

    **Troubleshooting Steps:**
    1. **Check App Version:** Ensure you have the latest version from the app store
    2. **Restart the App:** Close completely and reopen the application
    3. **Check Storage:** Make sure you have sufficient device storage (at least 1GB free)
    4. **Photo Size:** Try uploading smaller photos (under 10MB each)
    5. **Network Connection:** Ensure you have a stable internet connection

    **If the issue persists:**
    - Try uploading one photo at a time instead of multiple
    - Clear the app cache in your device settings
    - Restart your device

    If none of these steps resolve the issue, please let me know your device type and OS version, and I'll escalate this to our technical team for further investigation.
    """.strip(),
    ),
]

agent_pe = Agent(
    name="prompt engineering",
    model=Groq(id="openai/gpt-oss-20b", api_key=os.getenv("GROQ_API_KEY")),
    additional_input=support_examples,
)

# Demo: RAG
knowledge = Knowledge(
    vector_db=LanceDb(
        table_name="arxiv_knowledge",
        uri="tmp/lancedb",
        search_type=SearchType.vector,
        embedder=GeminiEmbedder(id="gemini-embedding-001", api_key=os.getenv("GEMINI_API_KEY")),
    )
)

_knowledge_loaded = False

async def load_knowledge_if_needed():
    """Load knowledge content asynchronously when needed."""
    global _knowledge_loaded
    if not _knowledge_loaded:
        await knowledge.add_content_async(
            path=f"{os.getcwd()}/2509.10402v1.pdf",
            reader=PDFReader()
        )
        _knowledge_loaded = True

agent_rag = Agent(
    name="rag",
    model=Gemini(id="gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY")),
    knowledge=knowledge,
    add_knowledge_to_context=True,
    search_knowledge=False,
)


agent_os = AgentOS(agents=[
    agent_blackbox,
    agent_pe,
    agent_rag,
])

app = agent_os.get_app()

# Add startup event to load knowledge
@app.on_event("startup")
async def startup_event():
    """Load knowledge on an application startup."""
    await load_knowledge_if_needed()

if __name__ == "__main__":
    # The default port is 7777; change with port=...
    asyncio.run(agent_os.serve(app="main:app"))