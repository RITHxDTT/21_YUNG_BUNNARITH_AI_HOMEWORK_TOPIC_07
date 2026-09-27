
Shopping Agent

agent uses **Ollama (`llama3.2:3b`)** as the local LLM and uses **PostgreSQL** for storing product data.

The agent can:
- Search products
- Check product stock
- Delete a product
- Check user permission before using a tool
- Ask for human approval before a destructive action

There are two roles:
- **Customer** - can search products and check stock
- **Admin** - can search, check stock, and delete products

For delete operations, the agent will ask the user to approve the action before it continues.

## How to Run

### 1. Create environment file

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Start PostgreSQL

The PostgreSQL database runs with Docker Compose.

```bash
docker compose up -d
```

The `init.sql` file will create the product table and insert sample data when the database is initialized for the first time.

### 3. Create Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Pull the Ollama model

```bash
ollama pull llama3.2:3b
```

### 6. Run the project

```bash
python main.py
```

After running the project, choose a role:

```text
Choose role (customer/admin): customer
```

Example questions:

```text
Find me a laptop.

Find me a laptop that is currently in stock.

Check stock of product 1.
```

For admin:

```text
Delete product 5.
```

If the action is destructive, the program will ask:

```text
Approve this action? (yes/no):
```

Type `exit` to stop the program.

