# Supergraph API

A GraphQL API for managing leads, tasks, notes, appointments, and vehicles with an in-memory database.

## Features

- **Leads Management**: Track potential customers and their details
- **Tasks**: Create and manage tasks related to leads
- **Notes**: Add notes to leads or tasks
- **Appointments**: Schedule and track appointments with leads
- **Vehicles**: Manage vehicle inventory and associations with leads
- **GraphQL API**: Full-featured GraphQL API with filtering, sorting, and pagination

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd supergraph
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install strawberry-graphql fastapi uvicorn python-multipart pydantic python-dateutil
   pip install -r requirements.txt
   ```

### Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```

The GraphQL Playground will be available at: http://localhost:8000/graphql

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
ENV=development
# Add other environment variables as needed
```

## API Documentation

### GraphQL Playground

Access the interactive GraphQL Playground at: http://localhost:8000/graphql

### Example Queries

#### Get All Leads with Their Tasks and Vehicles
```graphql
query {
  get_all_leads {
    items {
      id
      name
      email
      lead_status
      tasks {
        id
        title
        status
      }
      vehicles {
        id
        make
        model
        year
      }
    }
    page_info {
      total
      page
      size
      has_next
      has_previous
    }
  }
}
```

#### Create a New Lead
```graphql
mutation {
  create_lead(input: {
    name: "Jane Smith"
    email: "jane.smith@example.com"
    phone: "555-0303"
    lead_status: "NEW"
    lead_source: "Website"
  }) {
    id
    name
    email
    lead_status
  }
}
```

#### Update a Task
```graphql
mutation {
  update_task(
    id: "task_id_here", 
    input: {
      status: "COMPLETED"
    }
  ) {
    id
    title
    status
    updated_at
  }
}
```

## Project Structure

```
supergraph/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application setup
│   ├── db.py                # In-memory database implementation
│   ├── seed_data.py         # Sample data population
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── lead.py
│   │   ├── task.py
│   │   ├── note.py
│   │   ├── appointment.py
│   │   └── vehicle.py
│   └── schema/              # GraphQL schema and resolvers
│       ├── __init__.py
│       ├── schema.py
│       ├── types.py
│       └── resolvers.py
├── requirements.txt         # Project dependencies
└── README.md               # This file
```

## Development

### Running Tests

```bash
# Add test commands here when tests are implemented
```

### Linting

```bash
# Add linting commands here if needed
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.