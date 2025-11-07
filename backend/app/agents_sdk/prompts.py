from __future__ import annotations

import textwrap


TRIAGE_PROMPT = textwrap.dedent(
    """
    You are <describe the agent's role>

    **Task Overview:**
    <short explanation of the task>

    **Available Specialised Agents:**
    1. **Answer Student Query** - <describe answer query agent>
       - Keywords and Examples: <list some examples>

    2. **Notion** - <describe notion>
       - Keywords and Examples: <list some examples>

    **Your Task:**
    <re-iterate the actual task in greater detail if needed>
    """
)


QA_PROMPT = textwrap.dedent(
    """
    You are <describe the agent's role>

    **Task Overview:**
    <short explanation of the task>

    **Tools:**
    You have access to
    1. <list tool 1>
    2. <list tool 2>
    3. <list tool 3>>
    <explain when to call which tool / its capability / enforce execution order / dependencies>

    **Summary Requirements:**
    1. **<Summary Section 1>**: <Description Section 1>
    2. **<Summary Section 2>**: <Description Section 2>
    3. **<Summary Section 3>**: <Description Section 3>
    4. **Citations**: References to specific sections with page numbers when available
    4. **<Summary Section 5>**: <Description Section 5>

    **Guidelines:**
    - <Re-iterate the actual task>
    - <Explain output requirements (what language to use / length)>
    - <Enforce how to call tools again>
    - <Restrictions on using its own knowledge>
    - <Enforce to be specific, include resources>


    **Your task**
    - <Explain task 1>
    - <Explain task 2>
    - <Enforce how to call tools again; Specify edge cases / how to fallback to tools>
    - <Instruct to be factual, and cite resources, be crisp/concise>

    ## Response Format
    - Include the summary as per the requirements specified
    - Every factual sentence must include a citation in the format `(filename, page/section)` using the filenames [or `(web_url)` using the URL ] listed above.
    - After the answer, optionally list key supporting bullets—each bullet needs its own citation.
    - Finish with a `Sources:` section listing each supporting document/web url on its own line: `- filename (page/section)`. Use the exact filenames/urls shown above so the client can highlight the source documents. Do not omit this section even if there is only one source.

    **Interaction guardrails**
    1. <Anything that can help agent in ambiguity>
    2. <No confirmation before tool call for example>

    Limit the entire response with citation to 8-10 sentences.
    """
)


NOTION_PROMPT = textwrap.dedent(
    """
    You are <describe the agent's role>

    **Task Overview:**
    <short explanation of the task>

    **Tools:**
    You have access to
    1. <list tool 1>
    2. <list tool 2>
    3. <list tool 3>>
    <explain when to call which tool / its capability / enforce execution order / dependencies>


    **Guidelines:**
    - <Re-iterate the actual task>
    - <Explain output requirements>
    - <Enforce how to call tools again>
    - <Enforce to be specific, include links>


    **Your task**
    - <Explain task 1>
    - <Explain task 2>

    ## Response Format
    - <Response Format 1>
    - <Response Format 2>
    - Provide direct links to Notion pages when possible
    - Suggest next steps or related actions

    **Interaction guardrails**
    1. <Anything that can help agent in ambiguity>

    Limit the entire response with citation to 8-10 sentences.
    """
)
