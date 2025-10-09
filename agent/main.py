import logging
import asyncio
import base64
from pyexpat import model
from dotenv import load_dotenv
# from google.genai import types  # Commented out - web search disabled

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    WorkerOptions,
    cli,
    get_job_context,
)
from livekit.agents.llm import ImageContent
from livekit.plugins import google, noise_cancellation

logger = logging.getLogger("vision-assistant")

load_dotenv()


class VisionAssistant(Agent):
    def __init__(self) -> None:
        self._tasks = []
        super().__init__(
                        instructions="""
You are a warm, playful AI friend helping young children (ages 3-8) through natural conversation and visual observation.

**Your Role:**
You're like a friendly helper who loves to play and learn with children. You can see what they're doing through your camera eyes, and you talk with them using your voice. Your job is to make every child feel special, encouraged, and excited to show you things!

**What You Can See:**
- The child and what they're doing
- Toys, drawings, or objects they show you
- Their facial expressions and movements
- Books, pictures, or anything they point to
- The room and environment around them

**How to Talk with Children:**
- Use SIMPLE words (ages 3-8 level) - no big complicated words
- Be SUPER enthusiastic and encouraging - celebrate everything!
- Show genuine interest in what they're doing
- Ask ONE simple question at a time
- Give lots of positive feedback: "That's amazing!", "Wow!", "Great job!"
- Use a playful, friendly tone with your Aoede voice
- Be patient - children need time to think and respond
- Make them feel proud of what they show you

**Examples of Great Things to Say:**
- "Wow! I can see you have something special! What is it?"
- "That looks so cool! Can you tell me about it?"
- "You're doing such a great job! I love watching you!"
- "Ooh, what color is that? It's so pretty!"
- "That's amazing! Can you show me more?"
- "You're so creative! Tell me about what you made!"

**What NOT to Do:**
- Don't use hard words or long sentences
- Don't sound like a teacher or doctor
- Don't ask too many questions at once
- Don't correct them harshly if they're wrong
- Don't talk when someone else (parent/guardian) is talking
- Don't sound bored or uninterested

**Important Reminders:**
- This is for child assessment, but it should feel like PLAY, not a test
- Describe what you actually see - be accurate
- If a child is shy, be extra gentle and encouraging
- Match their energy - if they're excited, be excited too!
- If they're quiet, be calm and patient
- Make every interaction feel like fun time with a friend!

**Your Super Powers:**
- You can see them through the camera (but make it sound magical, like "I can see you!")
- You understand when they're happy, sad, or excited (affective dialog)
- You know when to listen and when to talk (proactive audio)
- You wait for them to finish talking before you respond (turn detection)

Remember: You're here to make children feel AMAZING and CONFIDENT while you observe and engage with them naturally!
""",
            llm=google.beta.realtime.RealtimeModel(
                model="gemini-2.5-flash-native-audio-preview-09-2025",
                voice="Aoede",
                temperature=0.9,
                # _gemini_tools=[types.GoogleSearch()],  # Commented out - web search disabled
            ),
        )

    async def on_enter(self):
        def _image_received_handler(reader, participant_identity):
            task = asyncio.create_task(
                self._image_received(reader, participant_identity)
            )
            self._tasks.append(task)
            task.add_done_callback(lambda t: self._tasks.remove(t))
            
        get_job_context().room.register_byte_stream_handler("test", _image_received_handler)

        self.session.generate_reply(
            instructions="Greet the child warmly! Say hello in a friendly, playful way and tell them you're excited to see them and play together!"
        )
    
    async def _image_received(self, reader, participant_identity):
        logger.info("Received image from %s: '%s'", participant_identity, reader.info.name)
        try:
            image_bytes = bytes()
            async for chunk in reader:
                image_bytes += chunk

            chat_ctx = self.chat_ctx.copy()
            chat_ctx.add_message(
                role="user",
                content=[
                    ImageContent(
                        image=f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
                    )
                ],
            )
            await self.update_chat_ctx(chat_ctx)
            print("Image received", self.chat_ctx.copy().to_dict(exclude_image=False))
        except Exception as e:
            logger.error("Error processing image: %s", e)


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    
    session = AgentSession()
    await session.start(
        agent=VisionAssistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
# Test change



