"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    from runtime import TransientError
    attempts = data['max_attempts']
    if type(attempts) is not int or not 1 <= attempts <= 3:
        raise ValueError('max_attempts must be 1 to 3')
    for attempt in range(attempts):
        try:
            answer = await agent.ask('answer', 'Answer this SDK configuration question briefly.', data['request'], 'tools determines availability; allowed_tools determines automatic permission.')
            return {'answer': answer, 'attempts': attempt + 1}
        except TransientError:
            agent.event('retry_scheduled', stage='answer', attempt=attempt + 1)
            if attempt + 1 == attempts:
                raise
            await asyncio.sleep(.01 * 2 ** attempt)
    raise RuntimeError('Unreachable retry state')
