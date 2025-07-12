# 🧙‍♂️ ManuAI - AI Agent for Database Conversations

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-orange.svg)](https://github.com/astral-sh/ruff)

ManuAI is an intelligent AI agent that enables natural language conversations with your database. It combines the power of Large Language Models (LLMs) with advanced database optimization techniques to provide fast, accurate, and contextual responses to your data queries.

## ✨ Features

### 🤖 Conversational AI
- **Natural Language Processing**: Ask questions in plain English
- **Dual Capabilities**: Business intelligence expert + friendly conversation partner
- **Wizard-themed personality**: Engaging and helpful interactions
- **Context-aware responses**: Maintains conversation history

### 🗄️ Database Intelligence
- **Multi-database support**: Works with SQLite and other SQL databases
- **Schema analysis**: Automatically understands your database structure
- **Query optimization**: Intelligent query generation and optimization
- **Performance monitoring**: Real-time performance tracking and analytics

### 🚀 Performance Optimization
- **Dynamic complexity routing**: Automatically selects appropriate LLM based on query complexity
- **Query execution optimization**: Advanced caching and performance tuning
- **Smart model selection**: Balances accuracy and speed
- **Real-time dashboard**: Monitor performance metrics and optimization history

### 🔧 Advanced Features
- **Fine-tuning capabilities**: Improve model performance with custom training
- **Business intelligence**: Advanced analytics and reporting
- **Performance dashboard**: Visual monitoring and metrics
- **Extensible architecture**: Easy to customize and extend

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- uv package manager (recommended) or pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd manuai
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running the Application

#### Streamlit Web Interface
```bash
# Start the main application
uv run streamlit run app.py

# Or start the performance dashboard
uv run streamlit run dashboard.py
```

#### Command Line Interface
```bash
# Initialize database
uv run python bin/create-database

# Run optimization
uv run python optimize.py --production

# Show performance stats
uv run python optimize.py --show-stats
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# LLM Configuration
OLLAMA_MODEL=llama3.1:8b


# Database Configuration
DATABASE_URL=sqlite:///data/ecommerce.sqlite

# Performance Settings
ENABLE_CACHING=true
CACHE_SIZE=1000
QUERY_TIMEOUT=30
```

### Performance Optimization
```bash
# Apply production optimizations
uv run python optimize.py --production

# Apply development settings
uv run python optimize.py --development

# Run database benchmark
uv run python optimize.py --benchmark
```

## 📊 Performance Dashboard

Access the performance dashboard at `http://localhost:8501/dashboard` to monitor:
- Query execution times
- Model performance metrics
- Optimization history
- Database statistics
- Cache hit rates

## 🏗️ Architecture

### Core Components

- **`manuai/agent.py`**: Main AI agent with conversation capabilities
- **`manuai/database_optimizer.py`**: Database query optimization
- **`manuai/smart_optimizer.py`**: Intelligent model selection
- **`manuai/performance_dashboard.py`**: Real-time monitoring
- **`manuai/business_intelligence.py`**: Advanced analytics

### Key Features

1. **Dynamic Model Selection**: Automatically chooses the best LLM based on query complexity
2. **Query Optimization**: Advanced caching and performance tuning
3. **Business Intelligence**: Comprehensive data analysis capabilities
4. **Fine-tuning**: Custom model training for improved performance

## 🔍 Usage Examples

### Basic Database Query
```python
from manuai.agent import ask

# Ask a natural language question
response = ask("Show me the top 5 customers by revenue")
print(response)
```

### Performance Optimization
```python
from manuai.optimizations import optimize_query_execution

# Optimize a specific query
optimized_query = optimize_query_execution(
    query="SELECT * FROM customers WHERE revenue > 1000",
    database_path="data/ecommerce.sqlite"
)
```

### Business Intelligence
```python
from manuai.business_intelligence import generate_insights

# Generate business insights
insights = generate_insights(database_path="data/ecommerce.sqlite")
```

## 📈 Performance Features

### Database Optimizations
- **Intelligent indexing**: Automatic index recommendations
- **Query caching**: Smart caching for frequently accessed data
- **Connection pooling**: Efficient database connection management
- **Execution plan analysis**: Query optimization insights

### LLM Optimizations
- **Model routing**: Dynamic selection based on query complexity
- **Response caching**: Cache similar queries for faster responses
- **Fine-tuning**: Custom model training for domain-specific improvements
- **Batch processing**: Efficient handling of multiple queries

## 🛠️ Development

### Development Setup
```bash
# Install development dependencies
uv sync --group dev

# Run linting
uv run ruff check .

# Run formatting
uv run ruff format .

# Run pre-commit hooks
uv run pre-commit install
```

### Project Structure
```
manuai/
├── app.py                    # Main Streamlit application
├── dashboard.py             # Performance dashboard
├── optimize.py              # Performance optimization scripts
├── manuai/                  # Core package
│   ├── agent.py            # Main AI agent
│   ├── database_optimizer.py # Database optimization
│   ├── smart_optimizer.py   # Intelligent model selection
│   ├── performance_dashboard.py # Monitoring dashboard
│   └── business_intelligence.py # BI capabilities
├── data/                    # Database files
├── logs/                    # Performance logs
└── assets/                  # Static assets
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔒 Data Privacy

ManuAI is designed with privacy in mind:
- **Local processing**: All data processing happens locally
- **No data transmission**: Your database content never leaves your environment
- **Secure connections**: All LLM communications use secure protocols
- **Audit logging**: Complete audit trail of all operations

## 📚 Documentation

- **[Performance Guide](PERFORMANCE.md)**: Detailed performance optimization guide
- **[API Reference](docs/api.md)**: Complete API documentation
- **[Examples](examples/)**: Usage examples and tutorials

## 🤝 Support

- **Issues**: Report bugs and request features on GitHub Issues
- **Discussions**: Join the community discussions
- **Documentation**: Check the docs for detailed guides

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) for LLM integration
- Powered by [Streamlit](https://streamlit.io/) for the web interface
- Optimized with [SQLite](https://sqlite.org/) for database operations
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output

---

<div align="center">
  <p>Made with ❤️ by the ManuAI team</p>
  <p>🧙‍♂️ <em>"Ask, and your database shall answer!"</em></p>
</div>