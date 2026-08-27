# Architecture Documentation

The backend follows the dependency direction:

```text
Interface -> Application -> Domain <- Infrastructure
```

The Domain layer is framework-free. Application use cases depend on domain abstractions,
and infrastructure adapters implement those abstractions. The frontend communicates with
the backend through versioned REST endpoints.

- [Constitution compliance checklist](constitution-compliance.md)
- [Local development setup](../development/local-setup.md)
