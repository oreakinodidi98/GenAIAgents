# Microsoft Azure AI Solution Notes

## Overview

This document covers Microsoft Azure AI services and their solutions for building intelligent applications. Azure offers a comprehensive suite of pre-built AI services that handle vision, language, speech, and generative AI tasks, eliminating the need to build AI models from scratch.

---

## Table of Contents

- [Microsoft Azure AI Solution Notes](#microsoft-azure-ai-solution-notes)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Azure AI Services Overview](#azure-ai-services-overview)
    - [Azure AI Vision Services](#azure-ai-vision-services)
    - [Azure AI Language Service (NLP - Natural Language Processing)](#azure-ai-language-service-nlp---natural-language-processing)
    - [Speech Services](#speech-services)
    - [Generative AI Solutions (OpenAI Service)](#generative-ai-solutions-openai-service)
    - [Document Intelligence Solution](#document-intelligence-solution)
    - [Knowledge Mining Solution](#knowledge-mining-solution)
  - [Planning, Creating and Deployment of Azure AI service](#planning-creating-and-deployment-of-azure-ai-service)
    - [Responsible AI](#responsible-ai)
    - [Creating an Azure AI Service Resource](#creating-an-azure-ai-service-resource)
    - [Endpoints](#endpoints)
    - [CI/CD for Custom AI Models](#cicd-for-custom-ai-models)
    - [Container Deployment](#container-deployment)
  - [Management, Monitoring, and Security](#management-monitoring-and-security)
    - [Configure Diagnostic Logging](#configure-diagnostic-logging)
    - [Monitoring](#monitoring)
    - [Manage Costs](#manage-costs)
    - [Account Keys and Endpoints](#account-keys-and-endpoints)
      - [Key Vault](#key-vault)
    - [Private Communication](#private-communication)
    - [Content Moderation Solutions](#content-moderation-solutions)
      - [AI content safety](#ai-content-safety)
    - [Analyze Images ( Implement Computer vision solutions)](#analyze-images--implement-computer-vision-solutions)
      - [Image Analysis](#image-analysis)
      - [Detect Objects and generate tags](#detect-objects-and-generate-tags)
      - [Pricing](#pricing)
      - [OCR](#ocr)
    - [Custom Computer Vision Models](#custom-computer-vision-models)
    - [Analyze Videos](#analyze-videos)
    - [Analyze Text by using Azure AI Language](#analyze-text-by-using-azure-ai-language)
    - [Process Speech by using Azure AI speech](#process-speech-by-using-azure-ai-speech)
    - [Translate Language](#translate-language)
    - [Language Understanding Models](#language-understanding-models)
    - [QnA Solutions](#qna-solutions)
    - [Azure AI Search](#azure-ai-search)
    - [Document Intelligence](#document-intelligence)
    - [OpenAI Services](#openai-services)
  - [Demo](#demo)
    - [Set Up](#set-up)
    - [Troubleshooting](#troubleshooting)

---

## Azure AI Services Overview

Azure AI services are advanced algorithms and tools designed to process different types of data and enable intelligent applications. Below are the core service categories:

### Azure AI Vision Services

**Purpose**: Advanced algorithms that process and analyze images to extract information and insights.

**Four Main Categories**:

1. **OCR (Optical Character Recognition)**
   - Extracts text from images (supports both printed and handwritten text)
   - Supports over 150+ languages
   - Use cases: Digitizing documents, automating data entry

2. **Image Analysis**
   - Generates alt text for images (captions) for accessibility
   - Content moderation to identify inappropriate or sensitive images
   - Useful for web applications and content management systems

3. **Face Recognition**
   - Verifies and identifies users based on facial features
   - Liveness detection (distinguishes between static images and live individuals)
   - Privacy-limited capabilities due to regulatory and ethical concerns

4. **Video Analysis**
   - Detects presence and movement within video content
   - Tracks objects and analyzes temporal patterns
   - Applications: Security, behavior analysis, activity recognition

---

### Azure AI Language Service (NLP - Natural Language Processing)

**Purpose**: Enables computer/AI services to understand human text, analyze meaning, and derive intent.

**History**: Previously offered as separate services:
- Text Analytics
- QnA Maker
- LUIS (Language Understanding Intelligent Service)

These have been **merged into a unified Language service** with both pre-configured and customizable options.

**Key Capabilities**:

1. **Entity Linking**
   - Extracts entities from text and links them to Wikipedia references
   - Helps identify real-world objects and concepts

2. **Language Detection**
   - Determines the language of input text
   - Supports multiple language identification

3. **Key Phrase Extraction**
   - Identifies important topics and main themes from text
   - Extracts user intentions

4. **Named Entity Recognition (NER)**
   - Pulls out specific entities: names, places, cities, companies
   - Useful for data extraction and categorization

5. **Orchestration Workflow**
   - Creates directed conversations and chatbots
   - Routes requests to appropriate services

6. **PII (Personally Identified Information) Detection**
   - Identifies and redacts sensitive information (SSN, credit cards, emails)
   - Critical for compliance and privacy

7. **Sentiment Analysis and Opinion Mining**
   - Determines if text is positive, negative, or neutral
   - Useful for customer feedback analysis

8. **Document and Conversation Summarization**
   - Generates concise summaries from long texts
   - Works with both written documents and conversation transcripts

**Custom Services**:

- **Custom Text Classification**: Train models on your own data to classify text into custom categories (e.g., "Relevant to Azure" vs "Not relevant")
  - Requires 100s of labeled samples for training
  
- **Custom Question Answering**: Build domain-specific chatbots trained on your content and knowledge base

---

### Speech Services

**Purpose**: Enables applications that require audio processing and speech capabilities.

**Core Capabilities**:

- Speech-to-Text: Converts audio to written text
- Text-to-Speech: Converts written text to natural-sounding audio
- Speech Translation: Translates audio while speaking, then converts to speech

**Common Use Cases**:

- Generating captions and subtitles for video content
- Creating audio content from text (accessibility)
- Real-time transcription of meetings and conversations
- Real-time translation for multilingual communication

---

### Generative AI Solutions (OpenAI Service)

**Purpose**: Leverages large language models for creative and conversational tasks.

**Key Applications**:

1. **Conversation AI**
   - Responds to open-ended questions in human-like manner
   - Powers chatbots and virtual assistants
   - Maintains context in multi-turn conversations

2. **Content Creation**
   - Generates text in creative formats (stories, articles, code)
   - Creates images from text descriptions
   - Automates content generation workflows

3. **Data Grounding (Retrieval-Augmented Generation - RAG)**
   - **Problem**: LLMs mimic human conversation but aren't databases, leading to hallucinations (fabricating facts)
   - **Solution**: Feed LLMs with exact, relevant data to ground answers in truth
   - **Result**: Accurate outputs based on your specific data rather than training data

---

### Document Intelligence Solution

**Purpose**: Analyzes documents using pre-built or custom models to extract structured data from unstructured documents.

**Supported Document Types**:

- Invoices (extract amounts, dates, vendors)
- Receipts (itemized details, totals)
- ID documents (licenses, passports)
- Contracts (key terms, clauses)
- Healthcare documents (medical records, prescriptions)
- Tax forms (income, deductions)

**Workflow**:

1. Import documents into Azure Blob Storage
2. Apply Document Intelligence to extract and structure data
3. Convert unstructured documents into usable, searchable data

**Model Types**:

- **Pre-built Models**: For common document types (invoices, receipts)
- **Custom Models**: For domain-specific documents (proprietary forms, contracts)

---

### Knowledge Mining Solution

**Purpose**: Builds a searchable, AI-enriched index from your own content using Azure AI Search.

**How It Works**:

1. **Data Sources**: Can work with multiple data types:
   - Unstructured data: Blob Storage (PDFs, images, documents)
   - Structured data: SQL Database, Azure Table Storage
   - Semi-structured data: Cosmos DB (JSON documents)

2. **Enrichment**: Apply other Azure AI skills to enhance data:
   - Extract text (OCR), sentiment, entities, key phrases
   - Create a richer, more searchable knowledge base

3. **Indexing**: Build an index of enriched data
   - Creates a "knowledge store" that powers intelligent search
   - Enables semantic search beyond keyword matching
   - Use skills to enrich data
   - Skillsets include:
     - Key phrases; Sentiment; Named entities; image cation; summarises of text; Language detectio or custom skills

**Use Cases**: Internal documentation search, customer support knowledge bases, research databases

---

## Planning, Creating and Deployment of Azure AI service

> **Note**: This section covers strategies for planning and deploying Azure AI services. Include topics such as:
> - Responsible AI principles
> - Create an Azure AI resource
> - Container Deployment
> - CI/CD
> - Configuring API keys and endpoints

### Responsible AI

**Purpose**: Establishes ethical frameworks and governance for safe, trustworthy AI deployment that respects human values and legal requirements.

**Why It Matters**:

AI systems have real-world impacts across critical domains:
- **Police/Military**: Autonomous decision-making in high-stakes scenarios
- **Business**: Job applications and hiring decisions (risk of discrimination)
- **Finance**: Loan approvals automated by algorithms (denying credit unfairly)
- **Healthcare**: Medical diagnosis and treatment recommendations

Deploying AI irresponsibly can perpetuate bias, violate privacy, and cause harm.

**Six Responsible AI Principles**:

1. **Fairness**
   - Ensures AI treats individuals and groups equitably
   - Prevents discrimination based on protected attributes (race, gender, age, etc.)
   - Example: Hiring algorithms shouldn't discriminate against protected groups

2. **Inclusiveness**
   - Considers needs of diverse users and contexts
   - Ensures accessibility for people with disabilities
   - Avoids marginalizing underrepresented populations

3. **Reliability and Safety**
   - AI systems perform consistently and predictably
   - Fail gracefully without causing harm
   - Undergo rigorous testing in production scenarios

4. **Transparency**
   - Users understand how AI made its decisions
   - Explainability allows humans to audit and challenge outcomes
   - Example: Loan denial should explain which factors led to rejection

5. **Privacy and Security**
   - Protects personal and sensitive data from unauthorized access
   - Complies with regulations (GDPR, CCPA, etc.)
   - Secure handling of training and inference data

6. **Accountability**
   - Clear responsibility chains: who is accountable for AI outcomes?
   - Human oversight for consequential decisions
   - Mechanisms to appeal or correct AI decisions

### Creating an Azure AI Service Resource

**Purpose**: Choose the right deployment model and security configuration for your AI needs.

**Resource Options**:

1. **Multi-Service Account (Azure AI Service)**
   - Single endpoint and API keys to access all Azure AI services
   - Ideal when: You need multiple AI capabilities and want unified management
   - Advantage: One endpoint, one key set, centralized billing
   - Disadvantage: Less granular control per service

2. **Individual Resources** (separate Vision, Language, Speech, etc.)
   - Separate endpoint and keys for each service type
   - Ideal when: You need specific services or want fine-grained control
   - Advantage: Often include free tier; better per-service configuration
   - Disadvantage: Multiple endpoints and keys to manage

**Networking Options**:

- **Public Endpoint** (Default)
  - Endpoints available across the entire internet
  - Easiest to set up but less secure for sensitive workloads
  
- **Virtual Network (VNet)**
  - Deploy to a specific Azure VNet (create new or use existing)
  - Restricts access to resources within the VNet
  - Useful for enterprise environments with network isolation requirements

- **Private Endpoint**
  - Point-to-point private connection using Azure Private Link
  - Most secure option; traffic doesn't traverse the public internet
  - Requires Private Link setup and DNS configuration

**Security & Identity**:

- **System-Managed Identity**
  - Azure automatically creates and manages an identity
  - Service assumes this identity to access other Azure resources
  - Simpler but less flexible

- **User-Managed Identity**
  - You create and manage the identity lifecycle
  - More control over permissions and lifecycle
  - Can be shared across multiple resources

### Endpoints

**Purpose**: Endpoint is the network address where you send requests to use an Azure AI service.

**Endpoint Format**:

```
https://<name_of_service_assigned>.cognitiveservices.azure.com
```

**Historical Context**: Prior to July 2019, endpoints were region-specific. Now all Azure AI endpoints follow a standardized global format.

**Authentication with Keys**:

- **Claims-Based Authentication**
  - You pass a secret API key with each request to authenticate
  - Key verifies you have permission to use that service

- **Key Management**
  - Azure provides **2 keys** for security and rotation purposes
  - Each key independently grants access to the service
  - You only need 1 key to make API calls
  - Rotate keys periodically for security:
    - Regenerate Key 1 while using Key 2
    - Switch applications to Key 2
    - Regenerate Key 2
    - Ensures zero downtime during key rotation

**Best Practice**: Store keys securely in Azure Key Vault, not in code

### CI/CD for Custom AI Models

**Purpose**: Automate the retraining and deployment of custom AI models without disrupting production service.

**Applicable Services** (services with custom model support):

- Custom Vision service
- Custom Speech
- Conversation AI / Chatbots
- Custom Document Intelligence

**Why CI/CD Matters for AI**:

Traditional software CI/CD deploys code changes. AI CI/CD also manages model lifecycle:
- Retrain on new data without manual intervention
- Validate model quality before deployment
- Compare model versions objectively
- Deploy only when improvements are confirmed

**Two Critical Data Types**:

1. **Training Data**
   - Contains full set of features/properties you want the model to predict
   - Used to teach the model the patterns
   - When new training data arrives → model gets retrained automatically
   - Larger, more representative training data = better model accuracy

2. **Testing Data**
   - Deliberately excludes the target field (what you're predicting)
   - Used to validate model performance on unseen data
   - Simulates real-world scenarios
   - Compares predictions against actual values to calculate error rates

**Model Validation Workflow**:

1. Retrain model with new training data
2. Test against testing dataset
3. Calculate error rate of new model
4. Compare error rate to previous model version
5. **Decision**:
   - ✅ If new model performs better → Deploy it to production
   - ❌ If new model performs worse → Keep previous model, investigate why

**Benefits**:

- Automated retraining prevents manual bottlenecks
- Data-driven deployment decisions (based on metrics, not hunches)
- Continuous improvement as new data arrives
- Zero downtime model updates

### Container Deployment

**Purpose**: Deploy Azure AI services as containerized applications in your own environment instead of relying solely on cloud-hosted endpoints.

**Why Run AI Services Locally?**

Azure AI services run in the cloud by default, but cloud deployment isn't always suitable. Key reasons to use containers:

- **Compliance**: Data residency requirements (keep data within country/region)
- **Security**: Sensitive data shouldn't traverse the internet; process locally
- **Performance**: Reduce latency by eliminating cloud round trips
- **Connectivity**: Run AI services offline or in air-gapped environments (e.g., satellite with intermittent internet)

**Important Billing Note**: Even when running containers offline, Azure collects usage metrics for billing purposes. You still pay per API call.

---

**Benefits of Container Deployment**:

1. **Immutable Infrastructure**
   - Full control over hardware your resources run on
   - Reproducible deployments across environments

2. **Data Control**
   - Keep sensitive data within your network
   - No data transmission to cloud endpoints
   - Compliance with data residency regulations

3. **Model Update Control**
   - Choose when to deploy new model versions
   - Don't auto-update; maintain stability
   - Test updates before rolling to production

4. **Portable Infrastructure**
   - Deploy containers anywhere: on-premises, VMs, Kubernetes, Edge devices
   - Consistent behavior across environments

5. **Performance (Throughput & Latency)**
   - No internet round-trip overhead
   - Faster inference for time-sensitive applications
   - Ideal for real-time processing

6. **Scalability**
   - Scale containers up/down based on demand
   - Orchestrate with Kubernetes for auto-scaling

---

**Supported Services & Capabilities**:

**Language Services** (containerized options):
- LUIS (Language Understanding)
- Key Phrase Extraction
- Language Detection
- Sentiment Analysis
- Named Entity Recognition (NER)
- Summarization (preview)
- Translation (gated/limited availability)

**Speech Services** (containerized options):
- Speech-to-Text
- Custom Speech-to-Text
- Language Identification

**Vision Services** (containerized options):
- OCR (Optical Character Recognition)
- Spatial Analysis

---

**Deployment Workflow**:

1. **Get Container Image**
   - Pull Docker image from Microsoft Container Registry
   - Image contains the pre-trained AI model

2. **Configure & Deploy**
   - Use existing Azure AI service key and endpoint
   - Mount image with authentication credentials
   - Deploy to your infrastructure (Docker, Kubernetes, etc.)

3. **Run Container**
   - Container starts and is ready to receive requests
   - Communicates via local endpoint (no internet required)

4. **Use Local Endpoint**
   - Applications call the containerized service instead of cloud endpoint
   - Same API interface as cloud version
   - No latency from internet travel

**Example Deployment Targets**:
- Docker on your server
- Kubernetes cluster (on-premises or cloud)
- IoT Edge devices
- Air-gapped data centers

---

## Management, Monitoring, and Security

> **Note**: This section covers operational aspects:
> - Configure Diagnostic logging
> - Implementing security best practices (managed identities, encryption)
> - Setting up audit logging and compliance controls
> - Managing costs and usage quotas
> - Protect account keys

### Configure Diagnostic Logging

**Purpose**: Centralize logs and metrics so you can audit usage, troubleshoot failures, and monitor service performance.

Azure Monitor provides a unified dashboard across Azure services. AI service telemetry appears in **Logs** and **Metrics**, but there is no single built-in "AI-only" report by default.

**How to enable diagnostics for an Azure AI service**:

1. Go to **Monitoring**.
2. Open **Diagnostic settings**.
3. Select the log/metric categories you need, such as:
   - Audit Logs
   - Request and Response Logs
   - Azure OpenAI Request Usage
   - Trace Logs
   - AllMetrics

**Routing options** (one or more destinations):
- Log Analytics workspace
- Storage account
- Event Hub
- Partner solutions

Azure Monitor commonly uses **Log Analytics** for querying and analysis.

**Cost note**: Storage and ingestion of diagnostic data incur additional cost.

### Monitoring

**Purpose**: Track service health, reliability, and usage over time.

Azure Monitor helps track health and usage for Azure AI services. In **Diagnostic settings**, you can verify which resources have diagnostics enabled.

Use either **Metrics** or **Logs** depending on what you need.

**Metrics**:
- Select a **Scope** first.
- Choose the resource type/resource.
- Build charts over a selected time range (24 hours is the default).
- Typical metrics include:
  - Latency (response time)
  - Successful calls
  - Data in
  - Data out

**Logs**:
- Query telemetry messages and events.
- Set the correct scope before querying.
- Use **KQL (Kusto Query Language)** for deep analysis.

### Manage Costs

**Purpose**: Control spend and optimize service usage.

- Each Azure AI resource has its own pricing model, including multi-service accounts.
- Many standalone services include a free tier.
- Multi-service accounts are generally standard tier only (no free tier).

Use **Cost Management + Billing** in Azure to:
- View usage trends
- Analyze cost breakdowns
- Download usage data for offline analysis

### Account Keys and Endpoints

**Purpose**: Provide the connection details your application needs to call Azure AI services securely.

The **Keys and Endpoint** menu provides:
- Endpoint URL
- Access keys

Applications call the endpoint and authenticate using one valid key.

#### Key Vault

Azure AI services support key-based authentication and identity-based access patterns.

**Best practices**:
- Protect API keys and never hard-code secrets in source code or config files.
- Use Azure Key Vault to store secrets and certificates securely.
- In Azure AI services, access keys are treated as secrets.
- After creating a Key Vault, grant yourself the required role assignment to access it.
- Update application code to retrieve secrets from Key Vault at runtime.

### Private Communication

**Purpose**: Limit exposure of AI services by routing traffic through private network paths.

**Recommended network approach**:

1. Create a **VNet** in your resource group.
   - VNets isolate and secure communication between Azure resources.
   - For testing, default VNet settings can create a subnet automatically.

2. In Azure AI service **Networking** settings, avoid default open access:
   - Default is often set to allow all networks (less secure).
   - Prefer **Selected networks and private endpoints**.
   - Add your VNet so apps/VMs in that network can access the service privately.
   - Optionally allow your current client IP for administrative access.

3. You can disable **public network access** entirely for stricter security.

**Private endpoint notes**:

- Uses Azure Private Link for private, point-to-point connectivity.
- Requires a VNet.
- Supports dynamic private IP allocation.
- Can use private DNS records for friendly endpoint resolution.
- Access still requires proper authorization.

---

### Content Moderation Solutions

> **Note**: Text moderation and Image moderation

#### AI content safety

- Azure AI Content Safety
- Monitoring content that is generated by generative AI or humans
- Detects and filters violent, hate, self harm , sexual content
- Monitors text, images and both
- Analyse human or AI generatied content
- Text moderation can moderate the following
  - Hate and fairnes
  - sexual
  - violence
  - self harm
- Can defime severity threshold
- Drags a slider to chose level from low to high threshold
- Happens in the content safety stoduio
- contentsafety.cognitive.azure.com
- Can use our own resource (single service resource)
- Moderate text content -> can chose a sample or test your own
- Image moderation
- Judge against the same categories but for images
- Can also get sample code -> shows the enpoints for your text and image safety

---

### Analyze Images ( Implement Computer vision solutions)

**Purpose**: Use Azure AI Vision to analyze image content, detect objects, generate captions, and extract text with OCR.

**Core Capabilities**:

- Analyze images for visual features and semantic meaning
- Build image processing pipelines for automation workflows
- Implement OCR to extract printed and handwritten text

**Practical Notes**:

- You can increase confidence thresholds to return only higher-confidence detections.
- You can generate captions that describe the image in natural language.
- Smart cropping and aspect-ratio-aware cropping are supported to keep important visual content in frame.

#### Image Analysis

**Image Inputs**:

- Azure AI Vision accepts multiple image formats for analysis.
- There are multiple API versions (commonly v3.2 and v4.0).

**Image requirements for v3.2**:

- JPG, PNG, GIF, or BMP
- Less than 4 MB
- Greater than 50 x 50 pixels
- Less than 10000 x 10000 pixels for OCR

#### Detect Objects and generate tags

**Tags**:

- Describe context and concepts in a visual image (for example: "beach", "outdoor", "vehicle").

**Objects**:

- Detect physical objects and return location using bounding boxes.

**Confidence behavior**:

- Detection is never 100% certain; results always include varying confidence scores.

#### Pricing

Select only the features you actually need to reduce cost, especially for high-volume image workloads.

#### OCR

**Read API**:

- The OCR API is called **Read**.
- It can extract printed and handwritten text in supported languages.

**How to test**:

- In Azure Vision Studio, you can choose predefined examples or upload your own images.

**Output format**:

- Results are returned in JSON format.
- The service processes image content from a URL and returns analysis response data.
- OCR creates bounding boxes around detected words/lines.
- Handwritten text is also supported.

---

### Custom Computer Vision Models

**Purpose**: Train and personalize vision models using your own labeled images for domain-specific recognition tasks.

Custom Vision enables you to build custom image models by assigning your own labels and training on your own datasets.

**Model types**:

1. **Image Classification**
    - Predicts which category an image belongs to.
    - Example: train labels for flower types, then predict the flower type in a new image.
    - Does not locate objects; it only predicts category labels.

2. **Object Detection**
    - Identifies and locates objects within an image.
    - Returns object location using **bounding boxes**.
    - Useful for custom product detection and inventory-style use cases.

**How to create a custom vision model**:

1. Collect images for training.
2. Choose model type: classification or object detection.
3. In Vision Studio, go to image analysis and customize models with your images.

**Dataset and labeling workflow**:

- Datasets are image collections used for training and testing.
- Store images in blobs (linked storage account).
- Labeling options:
   - Manual labeling
   - Azure ML data labeling project
- For Azure ML data labeling, create a workspace first.
- Define label categories before tagging images.
- Start labeling in Azure ML by assigning tags to each image.
- Import the generated **COCO** file back into Vision Studio.
- The COCO export creates JSON metadata used to train the model.

**Training and evaluation**:

- Train the model using the prepared dataset.
- Keep a separate test dataset that was not used for training.
- Longer training can improve results (training duration is configurable).
- After training, custom models include default evaluation using a subset of training data.
- You can also run evaluation with your separate test dataset for more realistic validation.

**Publishing and consumption**:

- After creating a custom model, it can be consumed with the correct credentials, endpoint URL, and model name.
- There is no single dedicated "publish" button in this flow; usage is driven by endpoint + model identification.
- Consume the custom vision model from applications by calling the appropriate endpoint.

### Analyze Videos

**Purpose**: Extract insights from videos and perform real-time spatial analysis using Azure AI video services.

Videos are conceptually a sequence of images; Azure AI applies frame-by-frame analysis to extract temporal patterns and insights.

**Two Core Services**:

1. **Azure AI Video Indexer**
   - Web app that analyses the full content of a video or live stream.
   - Portal: [videoindexer.ai](https://videoindexer.ai)
   - Extracts insights such as:
     - Transcripts (speech-to-text)
     - OCR (text visible in frames)
     - Faces (identification and tracking)
     - Topics (themes discussed)
     - Audio effects (music, noise, silence)
     - Text-based emotions (tone analysis)

2. **Azure AI Vision Spatial Analysis**
   - Detects presence and movement of people within a video.
   - Examines objects in a scene and their spatial relationships to each other.
   - Example: Retail store context — tracking customer movement and analyzing objects in a space.
   - Can be configured and tested in Azure Vision Studio.

### Analyze Text by using Azure AI Language

**Purpose**: Apply Natural Language Processing (NLP) to extract meaning, entities, sentiment, and sensitive data from text.

**Access methods**:
- Azure AI Language Studio
- REST API
- Docker container (for on-premises deployment)

**Prerequisite**: A Language resource (part of Azure Cognitive Services).

**REST API format**:
```
https://<endpoint>/language/:analyse-text
```
**SDK**: `Azure.AI.TextAnalytics`

---

**Key Text Analysis Capabilities**:

1. **Key Phrase Extraction**
   - Analyses text and extracts key concepts, themes, and phrases.
   - Provides insights into the main topics of a document.
   - Supports multiple languages.
   - More input text generally improves results.

2. **Entity Extraction (Named Entity Recognition)**
   - Identifies physical and real-world entities: people, places, objects, job titles, addresses, names, emails, events, phone numbers, skills, etc.
   - Can build a custom model for domain-specific entity types.
   - Testable in AI Language Studio.

3. **Sentiment Analysis and Opinion Mining**
   - Determines whether text is positive, negative, or neutral.
   - Returns a confidence score between 0 and 1.
   - Never 100% confident; always probabilistic.
   - Enabling **opinion mining** extracts additional insights (e.g., aspect-level sentiment).
   - Common use case: product reviews, social media monitoring.
   - Configurable in Language Studio.

4. **Language Detection**
   - Detects which language a piece of text is written in.
   - Supports more than 100 languages.
   - Handles languages with multiple scripts (e.g., Arabic can also be written in Latin script).
   - Returns a confidence score between 0 and 1.

5. **PII Detection (Personally Identifiable Information)**
   - Detects, blocks, and removes sensitive personal data from text.
   - Examples: phone numbers, names, email addresses, national IDs — anything that could identify an individual.
   - Critical for compliance, privacy, and data redaction workflows.

### Process Speech by using Azure AI speech

**Purpose**: Convert between spoken audio and text, and control speech synthesis output using Azure AI Speech services.

**Core Capabilities**:

1. **Text-to-Speech**
   - Converts written text into natural-sounding audio.
   - **Prosody**: models stress and intonation patterns in speech, making output sound more human and natural.
   - Supports customizable AI voices.
   - You can tune output parameters: rate, pitch, pauses, and more.
   - Use cases: voice assistants, accessibility, audio content generation.
   - Can also run in containers (local enviroment and reducing latency)
   - Falls under Responsible AI Guidlines
   - There is a speech studio
     - Need to creaate speech service and select resource to try itout
     - Can use Audio sample (pre build voices), human voices or customization

2. **Speech-to-Text**
   - Understang spoken human speech and been able to translate that
   - Converts spoken audio into written text.
   - Supports real-time and batch transcription.
   - can create a glossary for specific qords and provide alternatives of how to pronouce it
   - Use cases: transcription, voice commands, accessibility.
   - Real time speach, batch speach , transltion, assesment
   - Adds punction to text when translating or transcribing
   - Phrase list: put word in there that i think might appear and it will take it into consideration

3. **Speech Synthesis Markup Language (SSML)**
   - XML-based language for fine-tuning synthesized speech output.
   - Control speaking rate, pitch, pauses, pronunciation, and voice style.
   - Allows expressive and natural-sounding text-to-speech responses.
   - Define the emotion thats been expressed whilst you are talking
   - programming language , create text to speeach give clues to the AI on structure and how to say things

4. **Intent Recognition**
   - Combines speech-to-text with language understanding to detect a user's intent from spoken input.
   - Integrates with LUIS or Azure AI Language models.
   - Use cases: voice-driven applications, conversational AI.
   - Computer extracts and intention of what you want
   - 2 ways of doing this in Azure AI speech service
   - Pattern matching
     - Specific words and phrases triggerss the intenttion 
     - The user ha to be trained to tell the computer to do something
   Conversation Language understanding (CLU)
     - used to be called LUIS
     - User speech is transcribed into text
     - intetntion API with language service 
     - Take text and pass it to language service to get users intention
     - Needs to be trained does not come out of the box samples
     - Done through language studio not speech studio
     - Can use a Basic (demo) or Advanced Model to train

5. **Keyword Recognition**
   - Detects specific trigger words or phrases in a continuous audio stream.
   - Lightweight and can run on-device (edge).
   - Use cases: wake words (e.g., "Hey Cortana"), hotword detection.
   - Device is always listening
   - but not always sending what you are saying to the cloud
   - has on device key word recognition and then send to cloud to verify and to ac on the key word so speach to text which ten gets sent over to the service that determines the intention
   - Key word recognition is done on the cloud
   - Works in speach studio
     - create model, description and KEyword to activate this
     - then creates several pronounciations audio that you can agree or disagree to activate thisthen choose model type (Basic or advanced)then creates y word project allowing you to programm applications to react to key word

### Translate Language

**Purpose**: Translate text, documents, and speech using Azure AI Translator for multilingual applications.

**Core service**: Azure AI Translator (separate resource type from Azure AI Language resource).

**Key characteristics**:

- Pay-per-character pricing model
- Supports containerization
- Supports three translation patterns:
   - Synchronous
   - Asynchronous
   - Real-time

**Document Translation Workflow (Language Studio)**:

1. Use **Azure AI Translator** resource (not Language resource).
2. Enable managed identity (required for storage access).
3. Connect to a storage account.
    - Assign **Storage Blob Data Contributor** role to the translator identity.
4. Configure CORS (Cross-Origin Resource Sharing) on storage account.
    - For demos, you can allow all origins.
5. Select up to 10 target languages.
6. Upload source files and write outputs to a storage container.
7. Optionally add a glossary file for custom term translation.
8. Download translated results automatically when complete.

**Important constraints**:

- Managed identity is not available in all global-region scenarios.
- Free tier limitations apply to some translation workflows.

**Custom Translation**:

- Tune the model for your domain, industry, or business language.
- Training data options:
   - **Parallel documents**: paired source-target training sets (minimum around 10,000 sentence pairs).
   - **Dictionary data**: term-by-term custom mappings.
- Evaluation uses **BLEU score** (0-100); higher is better.

**Speech Translation Scenarios**:

1. **Speech-to-Speech**
    - Most complex scenario (for example, international conferences).
    - Single pipeline: speech-to-text -> text translation -> text-to-speech.

2. **Speech-to-Text Translation**
    - Simpler than full speech-to-speech.
    - Convert speech to text first, then translate text to target language.

3. **Multiple Target Languages Simultaneously**
    - Add multiple target languages in studio or API call.
    - Improves latency/user experience for multilingual audiences.
    - Cost still scales per character per target language (so it does not reduce cost).

### Language Understanding Models

**Purpose**: Understand user intent from natural language using Conversation Language Understanding (CLU).

**Platform note**:

- LUIS (Language Understanding) has been retired and replaced by **CLU**.

**Core concepts**:

- **Utterance**: What a user says or types.
- **Intent**: The action/task the app should perform.
   - **None intent**: default fallback when an utterance does not match any defined intent.
- **Entities**: Key data points extracted from utterances (for example: quantity, size, toppings, type).

**Data and labeling requirements**:

- Requires training data.
- Label utterances with intents.
- Tag entities manually in utterances.
- Minimum of 10 utterances to train a model.
- Availability is region-dependent.

**Building in Language Studio**:

1. Use a Language-type resource.
2. Create your catalog of intents.
3. In the Data tab, map utterances to intents.
    - Optionally use AI-assisted utterance suggestions.
4. Tag entity spans in the utterances.

**Training jobs**:

- Create a training job and give it a name.
- Model modes:
   - **Standard**: faster, English-only.
   - **Advanced**: more fine-tuned, multilingual, higher cost.
- Use data splitting to choose training vs testing percentages.
- Only one training job can run at a time.

**Deployment and testing**:

- Deploy trained models to test intent recognition behavior.
- Common use case: chatbot intent routing.

**Availability and resilience considerations**:

- Plan for backup and recovery.
- Maintain a hot backup in another region with the same model.
- Copy configuration/settings from source to backup region.
- Watch for configuration drift between regions.

### QnA Solutions

**Purpose**: Build low-code question answering chatbots using your own content in Azure AI Language Studio.

**What it is**:

- A chatbot-oriented question answering solution under Azure AI Language.
- Uses NLP to answer questions from your custom knowledge base.
- Best suited for relatively static information (content that does not change frequently).
- Typically returns consistent answers for the same question.

**Why use it**:

- Low-code setup experience.
- Easy integration with websites and bot front-ends.
- Supports structured conversation flow and follow-up prompts.

---

**Setup process**:

1. Create a new project in Azure AI Language Studio.
2. Connect or create an Azure AI Search resource.
3. Choose language settings for the project.
4. Set project name and default fallback answer.
5. Add sources for the knowledge base.

**Knowledge base content options**:

- Manual question-answer pairs.
- Imported external sources (auto-structure detection supported), such as:
   - Q&A files
   - Text files
   - PDF files
   - External URLs

---

**Testing and confidence tuning**:

- Test with generated `curl` commands from deployment/code samples.
- Test with the prediction URL directly.
- Adjust confidence threshold to control response acceptance.

**Deployment flow**:

1. Promote/copy knowledge base from test index to production index.
2. Integrate with Azure Bot Service (front-end bot layer).
3. Connect bot service to App Service (or your hosting layer).
4. Set Language resource key as an environment variable in App Service.

---

**Conversation design features**:

- **Multi-turn conversations**:
   - Add follow-up prompts.
   - Link follow-up paths to existing questions.

- **Alternate phrasing**:
   - Add alternate question phrasings.
   - Visualize intent/context tree.

- **Chit-chat personality**:
   - Add personality responses for more natural interactions.

**Backup and portability**:

- Export knowledge base as training data for backup.
- Export formats include Excel/TSV.

### Azure AI Search

**Purpose**: Build intelligent search experiences over your own data with full-text, vector, and semantic ranking capabilities.

**Background**:

- Azure AI Search (formerly Azure Cognitive Search) is a search engine for your own data.
- It supports traditional full-text search and modern vector search.
- It can ingest heterogeneous/unstructured content and make it searchable.

**Core capabilities**:

- Rich query syntax
- Indexing features such as chunking, OCR, and image description enrichment
- Semantic ranking using AI language understanding
- Security, scaling, and integration with other Azure services

**How it works**:

1. Connect data where it already exists.
2. Build a search index over that data.
3. Process user queries against the index.
4. Your app retrieves and displays results.

**Index internals**:

- Input text is tokenized and stored in an **inverted index**.
- Input vectors are stored in a **vector index**.

---

**Create an Azure AI Search service**:

- Service name becomes part of your endpoint URL.
- Pricing tiers include: Free, Basic, Standard, High Density, and Storage Optimized.
- Tier cannot be changed after deployment.
- One tier per region.

**Scaling model**:

- **Replicas** = query workers (2 or 3 replicas for stronger SLA scenarios).
- **Partitions** = index sharding across servers for larger indexes and higher throughput.

---

**Create data sources**:

Azure AI Search can index from several Azure data stores, including:

- Azure Blob Storage
- Azure Data Lake
- Azure SQL Database
- Azure Table Storage
- Azure Cosmos DB

Additional notes:

- JSON structures are commonly used to define and map data.
- Authentication can use managed identity or key-based access.

---

**Indexes (schema design)**:

An index is like a database schema for searchable content.

Define fields and properties such as:

- Field name
- Data type
- Retrievable
- Searchable
- Filterable
- Sortable
- Facetable

Field behavior:

- **Retrievable**: field can be returned to the UI/search result payload.
- **Searchable**: field participates in full-text matching.
- **Filterable**: field can be used to narrow result sets.
- **Sortable**: field can be used to order results.
- **Facetable**: field can power drill-down navigation/facets.

Design note:

- More fields increase index size and re-indexing time.
- Example fields: blob URL, author, creation date.

Index creation options:

- Manual schema creation
- Import-data wizard to scaffold index structure

**Enrichment during indexing**:

- Use OCR and other enrichment to combine text + image-derived content.

**Indexer**:

- A scheduled job that crawls source data and rebuilds/updates the index periodically.

---

**Skills and skillsets**:

- A **skillset** is a reusable collection of enrichment skills attached to an indexer.
- You can attach an Azure AI Services resource to run cognitive enrichments.

**Built-in skills** include:

- Key phrase extraction
- Custom entity lookup
- Language detection
- Entity linking
- Entity recognition
- PII detection
- Sentiment analysis
- Translation
- Image analysis
- OCR

**Built-in utility skills** include:

- Conditional skill
- Document extraction skill
- Text merge skill
- Shaper skill
- Split skill

**Custom skills**:

- Your own enrichment code for specific requirements.
- Exposed as a Web API called by the indexer.
- Operates on JSON payloads.
- Should run in the same region as the indexer for performance and reliability.

Enrichment outputs can be mapped into additional index fields.

---

**Run and query**:

1. Create and run an indexer.
2. Query the index using:
    - Search Explorer
    - REST API calls
    - A generated/demo app (for example, a simple HTML search UI)

### Document Intelligence

**Purpose**: Extract text, key-value pairs, layout, and structured data from documents using prebuilt or custom AI models.

**Background**:

- Azure AI Document Intelligence was previously called **Form Recognizer**.
- It is designed to turn semi-structured and unstructured documents into usable data.

**What it can do**:

- Extract text from documents
- Extract key-value pairs
- Analyze document layout and structure
- Classify document types
- Convert forms into structured data for storage or further processing

**Common document examples**:

- Invoices
- Utility bills
- Tax forms

---

**Model types**:

1. **Prebuilt models**
   - Ready-to-use models for common document types.
   - Good for fast setup and standard scenarios.

2. **Classification models**
   - Identify which type of document is being processed.

3. **Custom neural models**
   - Trained on a large collection of example data.
   - Useful when document formats vary but still follow learnable patterns.

4. **Custom template models**
   - Best when documents follow a consistent visual template.

5. **Custom composed models**
   - A collection of models grouped together for broader document handling.

---

**Provisioning and access**:

- Create a **Document Intelligence** resource in Azure.
- Use **Document Intelligence Studio** to test and build solutions.
- Studio URL: `documentintelligence.ai.azure.com`
- Access uses the usual **endpoint and key** model.

**Pricing tiers**:

- **Free tier** and **Standard tier** are available.
- Free tier includes around **500 pages per month**.

**Document limits**:

- Up to **2000 pages** for PDF processing.
- Free tier supports fewer pages per request (for example, up to 2 pages in some cases).

---

**Core capabilities in practice**:

- **Read**: extract text from documents
- **Layout**: detect structure, sections, tables, and arrangement
- **Text extraction / processing**: capture data that can be stored in a database or downstream system

**Typical workflow**:

1. Create a Document Intelligence resource.
2. Open Document Intelligence Studio.
3. Choose a capability such as Read, Layout, or a prebuilt/custom model.
4. Provide a document.
5. Review extracted text, fields, and structure.
6. Use the results in applications, workflows, or databases.

**Practical note**:

- You can test the experience in the studio using endpoint/key access, including scenarios where you have access to an existing resource.
- The end goal is to extract useful document data for further automation and processing.

### OpenAI Services

**Purpose**: Use Azure OpenAI Service to build generative AI applications for text, chat, retrieval-based answers, and image generation.

**What Azure OpenAI provides**:

- Access to powerful **Large Language Models (LLMs)**
- Human-like text generation
- Chat-based interactions
- Prompt-driven completions
- Retrieval-Augmented Generation (RAG)
- Fine-tuning and custom model adaptation
- Image generation with DALL-E

**Foundational concepts**:

- **LLM (Large Language Model)**: A model trained on massive amounts of text that can generate highly human-sounding responses.
- **Prompts and completions**: You give the model an input prompt, and it returns a completion/response.
- **Tokens**: Models have limits based on token count rather than raw characters or words.
- **Prompt engineering**: Adjust the prompt structure and instructions to produce the output you want.

**Historical note**:

- The idea of machine-generated text being indistinguishable from human conversation relates to the **Turing Test**.
- Modern public interest in generative AI accelerated significantly after ChatGPT was released in November 2022.

**RAG and fine-tuning**:

1. **Retrieval-Augmented Generation (RAG)**
    - Provides relevant source information as part of the model input.
    - Reduces hallucinations by grounding responses in trusted content.
    - Useful for enterprise knowledge bases and document-based assistants.

2. **Fine-tuning**
    - Takes an existing LLM and retrains/adapts it with additional task-specific data.
    - Produces a more specialized model for a domain or use case.
    - Typically a later-stage optimization after prompt engineering and RAG have been explored.

**Provisioning Azure OpenAI Service**:

1. Search for **Azure OpenAI** in Azure.
2. Create the resource.
    - Access is gated, so approval/justification may be required.
3. Pricing is generally **Standard tier** only (no free tier).
4. Networking can be restricted to selected networks/private access.
5. Manage model deployments in **Azure OpenAI Studio**.
    - Choose which model to deploy.
    - Each deployment creates an endpoint for inference.

**Models and deployments**:

- The **Quotas** tab shows which models and capacity you can access.
- **Deployments** are the actual callable model endpoints created inside your Azure OpenAI resource.

**Completion vs chat**:

1. **Completion-style generation**
    - Generates natural language from a plain prompt.
    - Does not inherently maintain chat context.
    - Without grounding or careful prompting, answers may hallucinate (make up information).

2. **Chat playground**
    - Better suited for conversational scenarios.
    - Includes:
       - **System message**: sets the assistant behavior/personality
       - User input
       - Parameter configuration
       - View code option for implementation examples

**Prompt and model configuration**:

- **Temperature** affects creativity/randomness.
- Different models produce different styles and quality of output.
- Chat playground is designed for multi-turn sessions rather than one-off messages.

**Image generation with DALL-E 3**:

- You can ask for an image in natural language.
- The model generates an image based on the prompt description.

## Demo

### Set Up

1. Go into C:\GenAI\Agents\learning\AI-102_Azure_AI\demo
2. Set up Virtual enviroment ```python -m venv agent_env``` then ```agent_env\Scripts\activate```
3. Install needed packages ```pip install langgraph langchain langchain-openai python-dotenv```
4. For Azure repeat but  install ```pip install azure-ai-projects azure-identity msrest azure-keyvault-secrets azure-identity azure-cognitiveservices-vision-computervision```
5. Create a requirements.txt from your current environment ```pip freeze > requirements.txt```
   1. Or Install packages from an existing ```pip install -r requirements.txt```
6. Start building

### Troubleshooting

- To allow foundry/AI service to enable API key authentication run the following

```az
# 1) Confirm the active subscription in Azure CLI
az account show --query "{sub:id, tenant:tenantId, name:name}" -o table

# 2) Save IDs
$sub = "cb5b077c-3ef5-4b2e-83e5-490cc5ca0e19"
$tenant = az account show --subscription $sub --query tenantId -o tsv

# 3) Login Az PowerShell using GUID tenant
Connect-AzAccount -Tenant $tenant -Subscription $sub

# 4) Verify Az context
Get-AzContext | Format-List Account, Subscription, Tenant, Environment

Get-AzCognitiveServicesAccount |
Where-Object { $_.DisableLocalAuth -eq $true -and $_.AccountName -and $_.ResourceGroupName -and $_.Id } |
ForEach-Object {
  Update-AzTag -ResourceId $_.Id -Tag @{SecurityControl='Ignore'} -Operation Merge | Out-Null
  Set-AzCognitiveServicesAccount -ResourceGroupName $_.ResourceGroupName -Name $_.AccountName -DisableLocalAuth $false | Out-Null
}
```