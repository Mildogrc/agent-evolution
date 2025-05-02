# Tool Chains, MCP, A2A, and Other Developments

>  Bohr was reported to have said, ["*Well, no, of course I don't actually believe in it* (superstition), *but I'm told it works even if you don't believe it.*"](https://uat.taylorfrancis.com/chapters/mono/10.4324/9780429037214-17/superstition-leszek-ko%C5%82akowski-agnieszka-ko%C5%82akowska) 


Whether you believe AI is a hoax, a hype, or the ultimate solution, its influence on mankind's future is inevitable. The pace of growth of AI capabilities is startling—startling enough to warrant significant inspection and abundant introspection. 

## The Coming of Agents

[Agents are at the forefront](https://globalventuring.com/corporate/information-technology/corporates-rush-to-invest-in-ai-agents/) of AI implementation projects owing to the ease of building components that can perform operations requiring language, reasoning, logical deduction, pattern recognition, and other areas which were historically [considered humans' forte](https://arxiv.org/html/2404.01869v2). In the beginning LLMs were pattern matchers that learned the statistical relevance between words, and being a chatbot that generated coherent volume of textual response. The emergence of reasoning was a [series of improvements](https://arxiv.org/abs/2206.07682) with techniques such as

- [Scaling up models]( https://arxiv.org/abs/2005.14165) enabled capabilities beyond pattern matching
- *[Transformers (attention mechanism)](https://arxiv.org/abs/1706.03762)* that allowed capturing long-range dependencies
- instruction tuning with high-quality reasoning Q&As *cf.* [FLAN collection](https://research.google/blog/google-research-2022-beyond-language-vision-and-generative-models/) 
- [Chain-of-Thought (CoT) prompting](https://arxiv.org/abs/2201.11903) that shows steps before answering

The agents, for the topic of this discussion, refer to agents backed by LLMs. So far a few different ways of building agents are envisioned: 1/ [toolchains](https://python.langchain.com/v0.1/docs/modules/agents/concepts/) that orchestrate operations using an LLM and APIs (for example, using [langchain](https://python.langchain.com/docs)), 2/ an LLM itself invoking APIs (for instance, [Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/harness-the-power-of-mcp-servers-with-amazon-bedrock-agents/) or any such agents that use [MCP](https://docs.anthropic.com/en/docs/agents-and-tools/mcp)), 3/ [multi-agents](https://cloud.google.com/discover/what-are-ai-agents), where many LLM/SLM based agents interacting with each other (for instance, using [A2A](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/).)

## Current State of Agent Development

Our experiments with agents of all complexities are available in our github. Our POV is that the agents can perform significant amount operations autonomously, and can be classified from *Level-1* to *Level-5* based on implementation complexity. We are writing a blog post on this topic, draft of which can be found in our repo.

As part of building a Level-1 agent, which we term `taskbots`, we took up the task of building a CRM client agent. The idea is that the agent can look at emails from clients (or potential clients), automatically extract the relevant information, and update CRM. 

Our sample implementation was to build a client for HubSpot CRM. Our efforts are in [this GitHub repo](). An outline of our implementation efforts is this:
1. We built code that is capable of creating and managing leads. We exposed two Python functions, `create_lead()` to create a new lead in the HubSpot, and `create_meeting()` to setup a meeting with the new lead. These functions took the necessary information in a key-value format: `{email:"<>", firstname:"", lastname:""...}`
2. We wrote an agent prompt asking it to parse an email from a potential lead, find the relevant data, call the tooling to create an entry in HubSpot.
3. 


