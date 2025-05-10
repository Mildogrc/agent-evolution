# Tool Chains, MCP, A2A, and Other Developments
<!-- TOC -->
* [Tool Chains, MCP, A2A, and Other Developments](#tool-chains-mcp-a2a-and-other-developments)
  * [The Coming of AI Agents](#the-coming-of-ai-agents)
  * [Experiments with Agents](#experiments-with-agents)
    * [Techniques of Agent Implementations](#techniques-of-agent-implementations)
    * [Single Agent vs. A2A](#single-agent-vs-a2a)
      * [Tool-chaining with an external LLM](#tool-chaining-with-an-external-llm)
      * [LLM with Tooling](#llm-with-tooling)
      * [LLM with MCP](#llm-with-mcp)
      * [LLMs with MCP Server](#llms-with-mcp-server)
  * [An Illustrative Example: CRM Automation Agent](#an-illustrative-example-crm-automation-agent)
    * [HubSpot Taskbot - Level-1 Agents](#hubspot-taskbot---level-1-agents)
    * [HubSpot FlowBot - Level-2 Agent](#hubspot-flowbot---level-2-agent-)
    * [HubSpot InsightBot - Level-3 Agent](#hubspot-insightbot---level-3-agent)
  * [Further Topics to Explore](#further-topics-to-explore)
    * [Cost Analysis](#cost-analysis)
<!-- TOC -->

There have been advancements in AI in the past four years, whose influence on mankind's future is significant and enduring. The pace of growth of AI capabilities is startling; startling enough to warrant significant inspection and abundant introspection. 


## The Coming of AI Agents

> For the topic of this discussion: The term *AI agents*, also commonly known as *autonomous agents*, or simply *agents*, refers to agents backed by LLMs. 

[AI Agents are at the forefront](https://globalventuring.com/corporate/information-technology/corporates-rush-to-invest-in-ai-agents/)  of AI implementation projects owing to the ease of building components that can perform operations requiring language, reasoning, logical deduction, pattern recognition, and other areas that were historically [considered humans' forte](https://arxiv.org/html/2404.01869v2).  In the beginning, LLMs were pattern matches that learned the statistical relevance between words and chatbots that generated coherent volumes of textual responses. The emergence of LLMs as drivers of autonomous agents, were due to 1/ stronger reasoning, 2/ instruction following, 3/ tool-use reasoning, 4/ code-generation. These changes were brought about in LLMs as a [series of improvements](https://arxiv.org/abs/2206.07682) with techniques such as

- [Scaling up models]( https://arxiv.org/abs/2005.14165) enabled capabilities beyond pattern-matching
- *[Transformers (attention mechanism)](https://arxiv.org/abs/1706.03762)* that allowed capturing long-range dependencies
- instruction tuning with high-quality reasoning Q&As *cf.* [FLAN collection](https://research.google/blog/google-research-2022-beyond-language-vision-and-generative-models/) 
- [Chain-of-Thought (CoT) prompting](https://arxiv.org/abs/2201.11903) that shows steps before answering


## Experiments with Agents

This blog post also aims to share our findings from experimenting with agents. Our efforts to build agents of all complexities are available on GitHub  [here](https://github.com/Mildogrc/agent-evolution). Our POV is that the agents can perform significant operations autonomously and can be classified from Level-1 to Level-5 based on implementation complexity. The goal is to keep this entry *'live'*, keeping it updated with results from our trials.

### Techniques of Agent Implementations
Agents can be realized with varying techniques, amongst which we discuss four techniques the authors consider to be common. So far, a few different ways of building agents have been envisioned, and the technology involves [toolchain libraries](https://python.langchain.com/v0.1/docs/modules/agents/concepts/) that orchestrate operations using an LLM and APIs (for example, using [langchain](https://python.langchain.com/docs), an LLM itself invoking tools or APIs (for instance, [Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/harness-the-power-of-mcp-servers-with-amazon-bedrock-agents/) or any such agents that use [MCP](https://docs.anthropic.com/en/docs/agents-and-tools/mcp)), and [multi-agents](https://cloud.google.com/discover/what-are-ai-agents), where many LLM/SLM based agents interacting with each other (for instance, using [A2A](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/).) 

### Single Agent vs. A2A
We realize that multi-agent solutions (with A2A) are complicated, as many challenges of distributed computing (consensus problems, Byzantine faults, stabilization challenges), which are amplified because of LLM challenges such as hallucinations and lack of contexts. 

Interestingly, many design principles of building systems apply in designing agent-based automation. Should there be a single agent capable of doing the entire workflow? Should many agents be cooperating? How will the agents cooperate with each other? *(Cf. orchestration and choreography in microservices architecture)*

We will treat A2A in later sections.

----
![Agent Deployments](images/agent_deploys.png)

----

The above diagram depicts the four most common patterns of agent deployment.

#### Tool-chaining with an external LLM
In this setup, an *orchestrator*--a custom tool-chain--is built to implement the logic of the agent, while integrating with all enterprise assets. A very naive approach, wherein only a few aspects of LLM are employed. Bulk of the logic, most of the business flow, and all integrations are retained in the orchestrator. Many RAG use cases, classical-AI use cases typically employ this use case. 

#### LLM with Tooling
In this setup, LLM drives the functionality of the agent. The LLM uses reasoning to decide on a sequence of actions, and employs tools provided. Typically custom tooling is built to enable LLM to leverage enterprise assets. All endpoints of enterprise assets--REST APIs, data stores, partner APIs--get custom tooling to allow LLMs to discover, connect, and leverage them.

#### LLM with MCP
[*"The Model Context Protocol (MCP) is an open standard that facilitates seamless integration between LLM applications and external data sources or tools."*](https://modelcontextprotocol.io/specification/2025-03-26/index)
In this utopian setup, every enterprise asset is already MCP enabled and expose an MCP endpoint. LLM can now discover these MCP endpoints, and use the relevant enterprise assets to execute the required use cases. 

#### LLMs with MCP Server
This is a  *middle-ground* implementation, wherein an MCP server, similar to an API gateway, exposes MCP endpoints abstracting the complex integrations behind the server. 


## An Illustrative Example: CRM Automation Agent
Our rudimentary implementations involved building agents for CRM demonstrating the capabilities of agents. To demonstrate the possibilities of implementing increasingly complex agents, we chose to implement agents that can manage customer relations. The chosen toolset was Python, Google ADK, Ollama, and Llama/Gemma/Gemini-Flash. The CRM solution was HubSpot. 

### HubSpot Taskbot - Level-1 Agents

As part of building a Level-1 agent, which we term `taskbots`, we took up the task of building a CRM client agent. TaskBots are aimed at automating simple, rule-based tasks. They employ LLMs or SLMs to leverage targeted set of features such as, language understanding, conversational ability, content generation, to achieve repetitive workflows with minimal decision-making. 

The idea was agent can look at emails from clients (or potential clients), automatically extract the relevant information, and update CRM.  Our efforts are in [this GitHub repo](https://github.com/Mildogrc/agent-evolution/tree/level-1-hubspot). An outline of our implementation efforts is this:
1. We built code that is capable of creating and managing leads. We exposed two Python functions, `create_lead()` to create a new lead in the HubSpot, and `create_meeting()` to set up a meeting with the new lead. These functions took the necessary information in a key-value format: `{email:"<>", firstname:"", lastname:""...}`
2. We wrote an agent prompt asking it to parse an email from a potential lead, find the relevant data, call the tooling to create an entry in HubSpot.


### HubSpot FlowBot - Level-2 Agent 
A FlowBot improves upon a TaskBot by implementing a multistep flow. 

In the case of the CRM example, a FlowBot, apart from entering the lead, also works to find a good time on the lead's calendar for a meeting -- discussion, demo, or any such encounters. The workflow could be defined to increase in complexity, with more steps added. For instance, the flowbot could use tools to gather more data and insights about the client and update the CRM. It could transcribe the calls and add the details and sentiment of the call to the CRM software.


### HubSpot InsightBot - Level-3 Agent
InsightBots augment and list the potential paths with insights based on real-time findings.
In the case of the CRM example, the InsightBot, apart from the actions of a FlowBot,

## Further Topics to Explore

The experiments sparked interesting insights and thought-provoking discussions, which needs further exploration.

### Cost Analysis
An interesting facet to address is analyzing the costs of various agent implementation patterns.

