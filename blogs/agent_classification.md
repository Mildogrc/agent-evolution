
# <p style="text-align: center;">_<span style="color:red;align=center">DRAFT</span>_</p>

<!-- TOC -->
* [<p style="text-align: center;">_<span style="color:red;align=center">DRAFT</span>_</p>](#p-styletext-align-center_span-stylecolorredaligncenterdraftspan_p)
  * [**AI Automation: From Simple Tasks to Full Autonomy**](#ai-automation-from-simple-tasks-to-full-autonomy-)
  * [AI Automation Level 1: _Task Bots_](#ai-automation-level-1-_task-bots_)
    * [Basic Automation to Streamlining Efficiency](#basic-automation-to-streamlining-efficiency-)
  * [AI Automation Level 2: _FlowBots_](#ai-automation-level-2-_flowbots_)
    * [Workflow Orchestration to Integrate Intelligent Decisioning](#workflow-orchestration-to-integrate-intelligent-decisioning)
  * [AI Automation Level 3: _InsightBots_](#ai-automation-level-3-_insightbots_)
    * [Decision-Augmenting AI that Optimizes processes in Real-Time](#decision-augmenting-ai-that-optimizes-processes-in-real-time-)
  * [AI Automation Level 4: _NeuroBot_](#ai-automation-level-4-_neurobot_)
    * [Autonomous Coordination and Management of Multiple Intelligent Systems](#autonomous-coordination-and-management-of-multiple-intelligent-systems)
  * [AI Automation Level 5: _SentientBot_](#ai-automation-level-5-_sentientbot_)
    * [Self-Learning & Autonomous AI – Complete Autonomy](#self-learning--autonomous-ai--complete-autonomy)
  * [Examples](#examples)
    * [Possibilities](#possibilities)
    * [Analysis](#analysis)
  * [Summary](#summary)
<!-- TOC -->

## **AI Automation: From Simple Tasks to Full Autonomy**  

This six-part series explores the increasing sophistication of AI automation, tracing its journey from basic task execution to fully autonomous, self-optimizing systems. This document explains the various classifications of AI automation from basic to complex, broken down in increasing levels of complexity. As the sequence of actions that are based on decisioning increases, the errors increase. Systems tend to gradually drift away from the target intent as the errors compound. Constant course correcting becomes more difficult as time goes by due to errors creeping into various facets of decisions.

The next five documents in this series will respectively discuss each of these complexity levels in detail. Where possible, a sample implementation is made available on github (work in progress)

## AI Automation Level 1: _TaskBots_

### Basic Automation to Streamlining Efficiency  

![Typical Level1 Architecture](images/Level1.png)

- **Focus:** Automates simple, rule-based tasks. 
- **Examples**:
  - _Customer Email Triaging_: LLMs analyze and categorize customer emails based on content and sentiment, automatically tagging or forwarding them.
  - _Appointment Scheduling_: A GenAI-powered chatbot interprets a patient's email and schedules with the appropriate physician.
- **Characteristics:** LLMs are ideal for repetitive workflows with minimal decision-making, improving efficiency without requiring advanced intelligence. They are also capable of tool-calling, where LLMs use external tools to augment their capabilities.
- **Role of GenAI**:
  1. _SLMs_ efficiently handle lightweight natural language queries, enabling chatbots to process common scheduling and email-related tasks.
  2. For most parts, the task bot could use purpose-built services, or a combination of all, to attain the set task.
  3. _LLMs_ might be used to enable more nuanced interactions, such as summarizing emails or extracting action items from meeting notes.

## AI Automation Level 2: _FlowBots_

### Workflow Orchestration to Integrate Intelligent Decisioning

![Typical Level-2 Architecture](images/Level2.png)

- **Focus:** Automates multi-step workflows
- **Examples**:
  - _CRM updates_: An LLM extracts key details from sales emails, transcribes call notes, and updates the CRM automatically.
  - _Inventory management_: AI predicts stock shortages by analyzing purchase patterns and supplier lead times, triggering automated restocking.
- **Characteristics**: Enhances efficiency by integrating multiple tools, providing actionable insights while requiring human oversight for complex decisions.  
- **Role of GenAI**
    1. SLMs assist in structured data processing, such as categorizing incoming requests or filtering CRM updates.
    2. LLMs generate summaries of customer interactions, flagging urgent issues or recommending the next best actions.
    3. GenAI models integrate with APIs to optimize inventory planning based on demand forecasts.

## AI Automation Level 3: _InsightBots_

### Decision-Augmenting AI that Optimizes processes in Real-Time  

![Typical Level-3 Architecture](images/Level3.png)

- **Focus:** Assists in decision-making through real-time data analysis for tasks. The architecture could start leveraging multiple agents communicating with each other.
- **Examples**:
  - _Dynamic pricing_: AI analyzes competitor pricing, market trends, and consumer demand to adjust product prices in real-time.
  - _Fraud detection_: GenAI detects anomalies in financial transactions by analyzing historical patterns and unstructured customer interactions.
- **Characteristics:** Manages moderately complex processes across different business functions, operating with partial autonomy to optimize outcomes.  
- **Role of GenAI**
  1. SLMs work within edge environments to flag suspicious transactions without heavy computational costs.
  2. LLMs process free-text insurance claims or fraud reports, correlating them with structured data for risk assessment.
  3. GenAI models synthesize insights across pricing, demand, and fraud signals, helping businesses react dynamically.

## AI Automation Level 4: _NeuroBot_

### Autonomous Coordination and Management of Multiple Intelligent Systems

![Typical Level-4 Architecture](images/Level4.png)

- **Focus:** Coordinates multiple AI agents to optimize complex systems
- **Examples**:
  - _Hospital bed management_: AI predicts patient admissions, optimizes resource allocation, and automates scheduling to maximize capacity.
  - _Supply chain logistics_: AI dynamically adjusts shipping routes based on traffic, weather, and warehouse stock levels.
- **Characteristics:** Adapts to unforeseen scenarios, employs advanced reasoning, and learns from past interactions to improve system performance over time.
- **Role of GenAI**
  1. SLMs assist in quick operational tasks like dispatch notifications and basic scheduling.
  2. LLMs analyze large datasets, predict demand surges, and suggest workflow adjustments.
  3. GenAI platforms integrate various agents (IoT sensors, logistics platforms, ERP systems) to automate decision-making with minimal human input.

## AI Automation Level 5: _SentientBot_

### Self-Learning & Autonomous AI – Complete Autonomy

![Typical Level-5 Architecture](images/Level5.png)

- **Focus:** Executes fully autonomous operations that continuously adapt and self-optimize, handling complex interdependent business processes
- **Examples**:
  - _AI-driven underwriting_: AI assesses risk, personalizes insurance policies, and continuously updates models based on new data.
  - _Autonomous retail_: AI-powered stores manage inventory, pricing, and checkout with minimal human intervention.
- **Characteristics:** It demonstrates exceptional intelligence, adaptability, and autonomy, maximizing efficiency. Like Level-1, it does not require human intervention; however, the class of problems is extremely complex.
- **Role of GenAI**
  1. SLMs process customer interactions, handling routine inquiries without requiring cloud-heavy resources.
  2. LLMs analyze policyholder histories, regulatory updates, and market trends to refine underwriting decisions.
  3. GenAI platforms orchestrate self-optimizing systems, enabling AI-driven warehouses and cashier-less retail environments.

## Examples

To better understand the classification of agents, let us look at a few examples from domains not based on science or math, where a rule-based system will not suffice: fashion design and surgery.

### Possibilities

**A level-1 agent** solves the problem where the task can be configured or set up as a strict workflow. For example, a cloth designer might upload a cloth design and instruct agent-powered robots to cut to various sizes or stitch the cloth per configuration. Similarly, a surgeon might set up a robot to apply sutures or close up a patient to finish a surgery. In these scenarios, the work can be defined as a sequence of steps, with minimal errors and deviations from the task flow.

**A level-2 agent** would increase in sophistication, where an admin sets up a plan, and the agent drives multiple systems as per sequence. A doctor would set up the sequence of events required for a surgery, or a fashion designer uploads the target fashion design, and hands over the agent to operate various machines.

**A level-3 agent** would further increase in sophistication. An agent plans to perform various tasks in sequence. It provides an approver with a plan, which could be altered or overridden. The agent analyzes the patient and sets up a surgery plan. Or, given a fashion trend in a particular line of clothing, the agent creates new designs and asks for approval or modifications.

**A level-4 agent** is primarily autonomous: it can plan and automatically decide the sequence of actions. An overseer/observer, who could abort the process, still provides a human override.

**A level-5 agent** is entirely autonomous, running an entire hospital or a fashion design company.

### Analysis

Of course, such agents are a long way away, though the distant future is getting closer rapidly. The example above is a futuristic view of what AI could once achieve. However, the concepts do apply to existing domains, and such implementations are possible, albeit at simpler levels. This git repo attempts to theorize, experiment, and realize such AI automation efforts.

## Summary

As AI automation advances and becomes part of solutions across all domains, it is vital to be aware of the increasing complexity of decision-making and the opportunities and challenges it brings. Understanding these five levels of automation helps organizations anticipate potential pitfalls, optimize workflows, and implement AI-driven solutions effectively. It is important to note that many techniques to achieve these various levels of agents are available, and new methods are continuously formulated. Whether these agents are driven by mechanisms outside of SLM/LLMs (eg., custom langchain implementations), or driven by LLMs (eg., MCP based implementation of Anthropic, or ), or any other techniques in between, the classification is intended to be an exploration of the possible sophistication in AI automation levels.

We will explore each level in depth in the upcoming documents, offering insights, examples, and practical implementations. Stay tuned for a deeper dive into the evolving landscape of AI automation.
