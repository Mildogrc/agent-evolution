# Tool Chains, MCP, A2A, and Other Developments
<!-- TOC -->
* [Tool Chains, MCP, A2A, and Other Developments](#tool-chains-mcp-a2a-and-other-developments)
  * [The Coming of AI Agents](#the-coming-of-ai-agents)
  * [Experiments with Agents](#experiments-with-agents)
    * [Techniques of Agent Implementations](#techniques-of-agent-implementations)
      * [Tool-calling with an external LLM](#tool-calling-with-an-external-llm)
      * [LLM with Tooling](#llm-with-tooling)
      * [LLM with MCP](#llm-with-mcp)
      * [LLMs with MCP Server](#llms-with-mcp-server)
    * [Comparison of Approaches](#comparison-of-approaches)
      * [Control vs Flexibility](#control-vs-flexibility)
      * [Development complexity](#development-complexity)
      * [Cost](#cost)
      * [Reliance on LLM Reasoning](#reliance-on-llm-reasoning)
  * [Security of AI Agents](#security-of-ai-agents)
  * [Observability of Agents](#observability-of-agents)
    * [History of Monitoring Agents](#history-of-monitoring-agents)
    * [Tools and Frameworks](#tools-and-frameworks)
  * [An Illustrative Example: CRM Automation Agent](#an-illustrative-example-crm-automation-agent)
    * [HubSpot Taskbot - Level-1 Agents](#hubspot-taskbot---level-1-agents)
    * [HubSpot FlowBot - Level-2 Agent](#hubspot-flowbot---level-2-agent-)
    * [HubSpot InsightBot - Level-3 Agent](#hubspot-insightbot---level-3-agent)
    * [Level-4 Agents (NeuroBots) and Level-5 Agents (AGI)](#level-4-agents-neurobots-and-level-5-agents-agi)
  * [Further Topics to Explore](#further-topics-to-explore)
    * [Cost Analysis](#cost-analysis)
    * [A2A Complexity](#a2a-complexity)
<!-- TOC -->


> Live content of the entry [here](https://github.com/Mildogrc/agent-evolution/blob/blogs/blogs/agent_application.md).

Significant advancements in AI have occurred in the past four years, and their influence on humanity's future is substantial and enduring. The pace of growth of AI capabilities is startling. It is alarming enough to warrant copious inspection and abundant introspection.


## The Coming of AI Agents

> For the topic of this discussion: The term *agents*, along with the terms *autonomous agents*, or *AI agents*, refers to standalone decision-making system that leverages LLMs. 

 [AI Agents are at the forefront](https://globalventuring.com/corporate/information-technology/corporates-rush-to-invest-in-ai-agents/)  of AI implementation projects owing to the ease of building components that can perform operations requiring language, reasoning, logical deduction, pattern recognition, and other areas that were historically [considered humans' forte](https://arxiv.org/html/2404.01869v2). Initially, LLMs were pattern matches that learned the statistical relevance between words and chatbots that generated coherent volumes of textual responses. The emergence of LLMs as drivers of autonomous agents was due to 1/ stronger reasoning, 2/ instruction following, 3/ tool-use rationale, and 4/ code-generation. These changes were brought about in LLMs as a [series of improvements](https://arxiv.org/abs/2206.07682) with techniques such as

- [Scaling up models]( https://arxiv.org/abs/2005.14165) enabled capabilities beyond pattern-matching
- *[Transformers (attention mechanism)](https://arxiv.org/abs/1706.03762)* that allowed capturing long-range dependencies
- instruction tuning with high-quality reasoning Q&As *cf.* [FLAN collection](https://research.google/blog/google-research-2022-beyond-language-vision-and-generative-models/) 
- [Chain-of-Thought (CoT) prompting](https://arxiv.org/abs/2201.11903) that shows steps before answering.

This series of blogs is an attempt to capture our experiments with developing agents: tools, techniques, challenges, and best practices.


> It is interesting that the original ideas for building AI-based autonomous software, which learns by observing and training, is 30+ years old! For example, the paper *Modeling Adaptive Autonomous Agents* by Pattie Maes, published in the early 1990s, defines adaptive, autonomous, and intelligent agents. She proposed an intelligent system that can effectively monitor and learn from observing its environment rather than requiring explicit programming or complex symbolic logic. Though we have made massive technological strides today, some of the problems identified decades ago are still relevant.

## Experiments with Agents

This blog post also aims to share our findings from experimenting with agents. Our efforts to build agents of all complexities are available on GitHub  [here](https://github.com/Mildogrc/agent-evolution). Our POV is that the agents can perform significant operations autonomously. Furthermore, they could be progressively classified from Level-1 to Level-5 based on problem/solution complexity and autonomy. The goal is to keep this entry *'live'* updated with trial results.

### Techniques of Agent Implementations
So far, engineers have envisioned a few different ways of building agents; let us look at the four most popular techniques. A typical implementation involves [tool-calling libraries](https://python.langchain.com/v0.1/docs/modules/agents/concepts/) that orchestrate operations using an LLM and APIs (for example, using [langchain](https://python.langchain.com/docs), an LLM itself invoking tools or APIs (for instance, [Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/harness-the-power-of-mcp-servers-with-amazon-bedrock-agents/) or any such agents that use [MCP](https://docs.anthropic.com/en/docs/agents-and-tools/mcp)), and [multi-agents](https://cloud.google.com/discover/what-are-ai-agents), where many LLM-based or SLM-based agents interacting with each other (for instance, using [A2A](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/).) 

----
![Agent Deployments](images/agent_deploys.png)

----

The above diagram depicts the four most common patterns of agent deployment.

#### Tool-calling with an external LLM
In this setup, an *orchestrator* (a custom tool-call chain) implements the logic while integrating with all enterprise assets and LLMs. This foundational approach uses a simple integration pattern, wherein only a few aspects of LLM are employed. The orchestrator retains most of the logic, most of the business flow, and all integrations. Many RAG and classical AI use cases typically employ this use case.

#### LLM with Tooling
In this setup, the LLM drives the agent's functionality. The LLM uses reasoning to decide on a sequence of actions and employs the tools provided. Typically, custom tooling enables LLMs to leverage enterprise assets. All endpoints of enterprise assets—REST APIs, data stores, and partner APIs—get custom tooling to allow LLMs to discover, connect to, and leverage them.

#### LLM with MCP
[*"The Model Context Protocol (MCP) is an open standard that facilitates seamless integration between LLM applications and external data sources or tools."*](https://modelcontextprotocol.io/specification/2025-03-26/index)
In this fully integrated vision, every enterprise asset is already MCP-enabled and exposes an MCP endpoint. LLM can now discover these MCP endpoints and use the relevant enterprise assets to execute the required use cases. 

#### LLMs with MCP Server
This is a middle-ground implementation in which an MCP server, similar to an API gateway, exposes MCP endpoints, abstracting the complex integrations behind the server. 

### Comparison of Approaches

#### Our Observations
* **Control vs Flexibility**
  * When LLM uses tool directly, we observed that if LLM is given an example dataset, LLM can easily identify the right content to send to the tool. 
  * Though the LLM capability gives more control to embed the tool directly, architecturally it does not appear clean. Adding MCP adds a level of indirection and necessary abstraction.
  * Google ADK is easier to install and run, and automatically comes with a runner that allows a web interface to chat with the agent.

* **Development Complexity**
  * We observed that developing MCP is not straightforward. The releases are still new (version 0.x), and when used with FastAPI, run into version incompatibility challenges. It took many attempts trying different versions to find the compatible library (refer to requirements.txt)
  * Though we started with uvicorn to run the MCP server, we realized the need ofa user interface  monitor the MCP server status. We switched from `uvicorn` to using `streamlit`, but required us multiple refactoring to fix the integration between FastMCP, FastAPI, and tools.


#### Reliance on LLM Reasoning

Papers on Autonomous AI, self-improving systems, and long-term AI strategy - research papers.

## Security of AI Agents

## Observability of Agents
Similar to ML and LLM-based solutions, agentic solutions need monitoring, debugging, and operational oversight. This requirement becomes extremely important in multi-agent situations where the interactions cannot be known beforehand. Many techniques of monitoring and managing are proposed, varying from custom tooling to building special monitoring agents (which themselves are based on LLMs/SLMs).

### History of Monitoring Agents
The requirement to monitor autonomous agents is an ongoing field of research, starting from [NASA's projects to space](http://www.ai.mit.edu/courses/6.834J-f01/Williams-remote-agent-aij98.pdf) to robotics to now AI agents. Foundational work for observability can be found in [DARPA's work in creating explainable AI](https://www.darpa.mil/research/programs/explainable-artificial-intelligence), symbolic/rule-based policies to create interpretable RL ([XRL](https://github.com/Plankson/awesome-explainable-reinforcement-learning)), and trying to define formal methods to verify agent behaviors.
Formal validation of Agent (and LLM) behavior is nascent, with much research ongoing.


### Tools and Frameworks
When writing this, there were many commercial and open-source options. 
Of the many, we focused on two notable ones that piggyback on OpenTelemetry: [Langfuse](https://aws.amazon.com/blogs/apn/transform-large-language-model-observability-with-langfuse/) and [TraceLoop's OpenLLMetry](https://www.traceloop.com/openllmetry).
LangFuse is an open-source framework that tracks inference, retrieved embeddings, API and tool usage, and more. Specifically for agents, LangFuse provides features such as tracing intermediate steps, debugging failures, evaluating responses, and providing benchmarks.
OpenLLMetry is also an open-source framework that adds LLM-specific metrics to OpenTelemetry: performance metrics (such as latency, token usage, and error rates) and behavior metrics (prompts, workflows, metadata).

Though there are other popular open source with more capabilities, such as [Helicone](https://helicone.ai), [Arize Phoenix](https://arize.com), [AgentOps](https://agentops.ai), it is better to choose a tool that is OpenTelemetry compatible. Most enterprises will already have infrastructure compatible with OpenTelemetry, and also most cloud and service providers are usually OpenTelemetry compatible. Read OpenTelemetry's comments on this topic [here](https://opentelemetry.io/blog/2025/ai-agent-observability/).

Refer to our git repo for examples of how to use Langfuse.



## An Illustrative Example: CRM Automation Agent
Our rudimentary implementations involved building CRM agents and demonstrating their capabilities. We chose to implement agents that can *manage customer relations* to demonstrate the possibilities of implementing increasingly complex agents. The toolset we chose was Python, Google ADK, Ollama, and Llama/Gemma/Gemini-Flash. The CRM solution was HubSpot. 

> *No pictures means it didn't happen*
> 
> *No working code means it didn't happen*


### HubSpot Taskbot - Level-1 Agents

As part of building a Level-1 agent (which we term `taskbots`), we built a CRM client agent. TaskBots aim to automate simple, rule-based tasks. Employing LLMs or SLMs to leverage targeted features like language understanding, conversational ability, and content generation to achieve repetitive workflows with minimal decision-making.

The idea was that an agent could look at emails from clients (or potential clients), automatically extract the relevant information, and update the CRM. Our efforts are in [this GitHub repo](https://github.com/Mildogrc/agent-evolution/). An outline of our implementation efforts is this:
1. We built code that is capable of creating and managing leads. We exposed two Python functions, `create_lead()`, to create a new lead in HubSpot, and `create_meeting()`, to set up a meeting with the new lead. These functions took the necessary information in a key-value format `{email:"<>", firstname:"", lastname:""...}`
2. We wrote an agent prompt asking it to parse an email from a potential lead, find the relevant data, and call the tooling to create an entry in HubSpot. After that it creates an entry in a local Postgres database with <`lead-id`, `user-name`, `user-email`> for future reference

We have two different implementations of Level-1 Agents: 
1. A Google ADK-based implementation that directly discovers and uses tools to create a lead based on emails, and 
2. an agent implementation that uses the same tool-calling via an MCP server.

---

| Level-1 Agent with direct tool-calling                                 | Level-1 Agent that uses MCP |
|------------------------------------------------------------------------|---|
| <img src="images/hstool1.png" alt="Agent + Tool-calling" width="600"/> | <img src="images/hstool2.png" alt="Agent + MCP Server" width="600"/> |

---

### HubSpot FlowBot - Level-2 Agent 
A FlowBot improves upon a TaskBot by implementing a multistep flow. 

In the CRM example, a FlowBot, besides entering the lead, also works to find a good time on the lead's calendar for further steps (discussion, demo, or any such encounter). We could add more steps to a FlowBot's workflow, increasing its complexity. For instance, the flowbot could use tools to gather more data and insights about the client and update the CRM. It could transcribe the calls and add the details and sentiment of the call to the CRM software.


### HubSpot InsightBot - Level-3 Agent
InsightBots augment and list the potential paths with insights based on real-time findings. 

In the CRM example, InsightBot plans a strategy to handle the lead. InsightBot might look at the leads holistically, do a background check, and devise the best way to handle them. Then, InsightBot prompts an approver to determine whether the plan needs changes or is good to execute. Once a human/admin finalizes the plan, InsightBot will manage it. 

> Considering the intricate nature of this project and our limited resources with a constrained timeframe, this represents an ambitious undertaking and a significant stretch goal for us.


### Level-4 Agents (NeuroBots) and Level-5 Agents (AGI)
The agent implementations could get more complex and more autonomous. A level-4 agent could coordinate with multiple AI agents to optimize complex processes. A level-5 agent could execute operations with full autonomy--it could continuously adapt and self-optimize, handling complex interdependent business processes.

In the CRM example, a level-4 agent—a highly complex agent (or set of agents)—would work with sales and marketing teams, augmenting their lead-finding by learning and adopting. The agent(s) could learn about potential leads, plan lead generation with similar leads, handle nurturing, prepare proposals, and even close the deal. 

A level-5 agent, a theoretical AGI, would be fully autonomous. They would handle everything from creating marketing campaigns to finding leads, contacting them, planning a strategy, scheduling meetings, demoing the products or services, and attempting to make a sale. They could even handle customer support.

## Further Topics to Explore

The experiments sparked interesting insights and thought-provoking discussions, which need further exploration and will be part of future blog posts.

### Cost Analysis
An interesting facet is analyzing the costs of various agent implementation patterns. Agents have both savings and overhead. The savings are in speed, agility, and elasticity; however, the price is the risk of bad decisions, missed actions, and computational complexity. What is the right balance? Individual enterprises will have to evaluate this before implementing the solution.

### A2A Complexity
We realize that multi-agent solutions (with A2A) are complicated. The inherent challenges in LLMs, such as hallucinations and lack of context, amplify many of the challenges of distributed computing (consensus problems, Byzantine faults, stabilization issues).

Interestingly, many design principles of building systems apply in designing agent-based automation. Should there be a single agent capable of doing the entire workflow? Should many agents be cooperating? How will the agents cooperate? *(Cf. orchestration and choreography in microservices architecture)*

We will treat A2A in later blog posts.




### References and Further Reading

**Academic Papers and Collections:**

* [*Modeling Adaptive Autonomous Agents*](https://direct.mit.edu/artl/article-abstract/1/1_2/135/2256/Modeling-Adaptive-Autonomous-Agents) by Pattie Maes (1993)
* **FLAN (Finetuned Language Net) Collection:**
    * [*Finetuned Language Models Are Zero-Shot Learners*](https://arxiv.org/abs/2109.01652) by Jason Wei, Maarten Bosma, Vincent Y. Zhao, Kelvin Guu, Adams Wei Yu, Brian Lester, Nan Du, Andrew M. Dai, Quoc V. Le (2021).
    * [*Scaling instruction-finetuned language models*](https://arxiv.org/abs/2210.11416) by Chung, H. W. et al (2022).
* **Research on Autonomous AI, Self-Improving Systems, Long-Term AI Strategy:**

**Organizational Projects and Initiatives:**

* **NASA's Projects (related to autonomous agents):**
    * [Remote Agent: To Boldly Go Where No AI System Has
 Gone Before](http://www.ai.mit.edu/courses/6.834J-f01/Williams-remote-agent-aij98.pdf) by  Nicola Muscettolay, P. Pandurang Nayak, Barney Pell, Brian C. Williams (1998)
* **DARPA's Work (Explainable AI, Interpretable RL):**
    *  *[DARPA’s explainable artificial intelligence (XAI) program](https://ojs.aaai.org/aimagazine/index.php/aimagazine/article/download/2850/3419)* by Gunning, David, and David Aha. AI magazine 40.2 (2019): 44-58.

**Tools, Frameworks, and Standards (Documentation/Websites):**

* **Model Context Protocol (MCP):**
    * _[MCP Specification](https://modelcontextprotocol.io/specification/2025-03-26)
* **OpenTelemetry:**
    * _Website:_ [https://opentelemetry.io/](https://opentelemetry.io/)
    * _Specific Comments:_ [OpenTelemetry's view](https://opentelemetry.io/blog/2025/ai-agent-observability/)
* **Langfuse:**
    * _Website:_ [https://langfuse.com/](https://langfuse.com/)
* **OpenLLMetry:**
    * [TraceLoop OpenLLMetry Website](https://www.traceloop.com/openllmetry)
    * [Github project](https://github.com/traceloop/openllmetry)

* **Helicone:**
    * _Website:_ [https://www.helicone.ai/](https://www.helicone.ai/)
* **Phoenix (from Arize AI):**
    * [Phoenix Arize Website](https://arize.com/phoenix)
    * [Github project for Arize](https://github.com/arize-ai/phoenix)

* **AgentOps:**
    * _Website:_ [https://agentops.ai/](https://agentops.ai/)

