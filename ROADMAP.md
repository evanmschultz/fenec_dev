# 🦊 Fenec Project Roadmap

## 🎯 Short-term Goals

### ⚖️ Single Source of Truth, Assurance of Summarization Mapping, and a Better Algorithm for Updating Only the Changes in the Codebase

-   [ ] Reconfirm that the summarization maps created are correct to any project's structure
-   [ ] Use ChromaDB, or a third (SQLite) database to store all of the data and be referred to as a single source of truth
    -   Note: This is especially needed when sharing projects across multiple machines as the GraphDB must be constructed on each machine. Any errors I am making in logic, any ideas to improve this, or ANY suggestions at all are welcome!
-   [ ] Implement a better algorithm for updating only the changes in the codebase
    -   With a single source of truth, codebase updates can be handled more effectively. By comparing the metadata from the codebase to the existing data in the database, you can ensure that only the necessary updates are made. This method replaces, updates, or removes outdated data as needed, reducing the need to manually run update before each git commit.
        -   For example, the codebase can be parsed, and all code blocks in the database updated accordingly. If a code block hasn’t changed, but its line numbers have, only that information is updated. This targeted updating process prevents unnecessary re-summarization of large portions of the codebase when minor changes, like a docstring update, are made in a single function within a module.

### 🧪 Testing and Quality Assurance

-   [ ] Add comprehensive unit tests throughout the Fenec project
-   [ ] Implement integration tests for core functionalities
-   [ ] Set up continuous integration (CI) pipeline

### 🛠️ API and CLI Enhancement

-   [ ] Expand API functionality to allow for greater user control
-   [ ] Improve CLI interface with more options and better documentation
-   [ ] Add error handling and user-friendly error messages

### 💬 Chat Enhancement

-   [ ] Add support for chat memory and further context management, e.g. user added doc's for third party libraries
-   [ ] Enhancement, overhaul, or elimination of the ChromaLibrarian for vector retrieval
-   [ ] Multi-turn agentic chat for better contextual understanding

### 🧠 LLM Integration

-   [ ] Add support for Anthropic's Claude
-   [ ] Integrate TogetherAI models
-   [ ] Improve Ollama integration and documentation

### 📦 Packaging and Distribution

-   [ ] Prepare Fenec for packaging and distribution on PyPI
-   [ ] Create comprehensive installation and setup documentation

## 🌟 Medium-term Goals

### 🔄 Language Rewrite

-   [ ] Evaluate pros and cons of rewriting in Go vs Rust
-   [ ] Plan and begin implementation of chosen language rewrite
-   [ ] Transition from LibCST to Tree-sitter for multi-language support

### 📊 Performance Optimization

-   [ ] Optimize code parsing and summarization processes, multi-threading and parallelization of both parsing and summarization
-   [ ] Implement caching mechanisms to reduce API calls and improve speed

### 🗃️ Database Improvements

-   [ ] Enhance ArangoDB integration for more efficient graph querying and use of graph based RAG
-   [ ] Support for additional graph and vector databases

### 🤖 Agentic Documentation Creation

-   [ ] Develop AI-driven documentation structure planning
    -   [ ] Implement user approval/alteration of proposed structure
-   [ ] Create AI-generated documentation system
    -   [ ] Develop section-by-section generation with user feedback loop
    -   [ ] Implement context-aware generation using previously approved sections

### 🔌 Integration and Plugins

-   [ ] Develop plugins for popular IDEs (VSCode, PyCharm)
-   [ ] Create integrations with common development tools (e.g., Git, Jira)

## 🚀 Long-term Goals

### 🔄 Language Rewrite

Maybe language rewrite is best as a long-term goal. It is easier to do sooner than later, and it will help us achieve our long-term goals. We will evaluate pros and cons of rewriting in Go vs Rust, plan and begin implementation of chosen language rewrite, and transition from LibCST to Tree-sitter for multi-language support.

### 🌐 Multi-language Support

-   [ ] Add support for JavaScript/TypeScript
-   [ ] Explore support for other popular languages (C++, Ruby, etc.)

### 🧠 Advanced AI Features

-   [ ] Implement code generation capabilities
-   [ ] Develop AI-assisted refactoring tools
-   [ ] Create an AI-powered code review system

### 🤝 Community and Ecosystem

-   [ ] Establish a contributor community and guidelines
-   [ ] Develop a plugin ecosystem for community-driven extensions
-   [ ] Create comprehensive documentation and tutorials for developers

## 🔄 Ongoing Tasks

-   [ ] Regular updates to supported LLM models and APIs
-   [ ] Continuous improvement of code summarization and chat capabilities
-   [ ] Performance optimization and bug fixes
-   [ ] Documentation updates and maintenance
-   [ ] Community engagement and support

This roadmap is subject to change based on user feedback, technological advancements, and project priorities. We welcome contributions and suggestions from the community to help shape the future of Fenec!
