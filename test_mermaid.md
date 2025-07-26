# Test Mermaid Diagram

This is a test document to demonstrate Mermaid diagram support.

## Flow Chart Example

Here's a simple flowchart:

```mermaid
graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> B
    C --> E[End]
```

## Sequence Diagram Example

And here's a sequence diagram:

```mermaid
sequenceDiagram
    participant User
    participant App
    participant Browser
    
    User->>App: Press 'o' key
    App->>Browser: Open HTML with Mermaid
    Browser->>Browser: Render diagram
    Browser-->>User: Display result
```

## Regular Code Block

This is just a regular code block, not a Mermaid diagram:

```python
def hello():
    print("Hello, World!")
```

## More Content

The Mermaid diagrams above will be:
- Shown as placeholders in the terminal view
- Fully rendered when you open in browser (press 'o') 