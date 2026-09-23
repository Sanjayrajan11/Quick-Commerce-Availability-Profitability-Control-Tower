# As-is process
```mermaid
flowchart LR
 A[Customer requests goods] --> B[Store checks stock]
 B --> C{Stock sufficient?}
 C -->|No| D[Offer replacement or leave units unfulfilled]
 C -->|Yes| E[Pick and pack]
 D --> E
 E --> F[Dispatch and deliver]
 F --> G[Finance reviews sales separately]
 G --> H[Teams react after shortages or margin erosion]
```
Pain points: disconnected unit and financial measures; stale stock coverage; comparison of store totals without workload context; promotion revenue reviewed without variable cost. These are fictional requirements, not claims about an actual company.
