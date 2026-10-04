# Everette Supporter IT Agent

An AI powered IT support assistant for everyday technology users. The goal is to make technical troubleshooting, programming help, and learning easier through a simple chat experience.

> **Project status:** Planning. This repository currently contains the project README; the application has not been implemented yet.

## Vision

Create and launch a website where a user can describe a technical problem in plain language and receive clear, useful feedback. The interface will center on a text box: the user enters a question or issue, and an AI agent reasons about the input and writes a response with explanations and possible next steps.

The experience is intended for casual and regular technology users, including people who may not know the technical terms for what is going wrong. Responses should be approachable, explain unfamiliar concepts, and offer steps at an appropriate level of detail.

## Goals

- Help with general IT and programming questions.
- Explain technical topics and terminology in plain language.
- Assist with debugging code, applications, and software behavior.
- Help users navigate common software and operating system tasks.
- Guide users through identifying bugs and diagnosing potential malware or other security concerns.
- Over time, account for relevant device hardware and operating system details when the user provides them or explicitly enables their collection.
- Support troubleshooting from basic problem descriptions through more technical material, potentially including machine code and binary analysis.

## Planned capabilities

The agent is intended to help investigate issues such as:

- Bugs, glitches, and application malfunctions
- Programming and software errors
- Malware concerns and suspicious behavior
- Stop errors, system errors, and crashes
- Operating system updates and system management
- Processor and hardware related problems
- Communication, internet connection, and networking issues

The agent should explain uncertainty and distinguish between likely causes and confirmed findings. It should not claim that a device is infected or that a diagnosis is certain based only on a short prompt.

## Planned architecture

| Component | Planned approach | Responsibility |
| --- | --- | --- |
| Frontend | React and JavaScript | Website UI, prompt input, and readable responses |
| Backend | Python API, using a fast framework such as FastAPI | Request handling, validation, orchestration, and provider integration |
| Language model | Gemini and/or the OpenAI SDK | Interpret user input and generate troubleshooting guidance |
| Data storage | Database or other suitable storage location (to be selected) | Store only the information needed for the product, such as conversations or configuration |
| Deployment | To be decided later | Host the website and API when the application is ready |

The frontend should communicate with the backend API. The backend should keep model credentials private, send appropriate requests to the selected model provider, and return the answer to the user interface. The initial implementation should avoid collecting device information automatically; any future system inspection should be transparent and require the user's consent.

## Prerequisites

Development prerequisites will be finalized when implementation begins. The planned stack suggests:

- Git for source control
- Node.js and npm for the React frontend
- Python for the backend API
- An API key for whichever model provider is configured (Gemini or OpenAI)
- A database choice once persistence requirements are defined

Keep API keys in local environment variables or a local `.env` file that is excluded from version control. Never commit secrets to the repository. A future `.env.example` should document required variable names without containing real credentials.

## Development roadmap

1. Define the first user journeys and the assistant's safety boundaries.
2. Create the React chat interface with a prompt box and response display.
3. Build the Python API endpoint that accepts a prompt and returns a model response.
4. Add one model provider, configuration, and clear error handling.
5. Decide whether conversation persistence is needed and select a storage option.
6. Add testing, privacy and security review, and deployment planning.
7. Consider optional hardware or operating system context only after the user experience and consent model are defined.

## Safety and privacy principles

- Treat model output as troubleshooting guidance, not a guaranteed diagnosis.
- Ask before taking actions that change files, settings, or system state.
- Do not run user-provided code or commands automatically.
- Treat potential malware cases cautiously and prioritize safe, reversible guidance.
- Explain what device or diagnostic information is requested and why before collecting it.
- Protect API keys and minimize storage of sensitive user information.

## Contributing

The project is at the planning stage. As the application is implemented, this README should be updated with the actual setup commands, environment variables, API routes, and deployment instructions.
