email-intelligence-hub/
├── install.sh
├── docker-compose.yml
├── .env.example
├── config/
│   ├── prometheus/prometheus.yml
│   ├── grafana/
│   │   ├── datasources/datasources.yml
│   │   └── dashboards/email-dashboard.json
│   ├── node-red/flows.json
│   └── ollama/Modelfile
├── scripts/
│   ├── setup.sh
│   ├── test-flow.sh
│   └── backup.sh
└── README.md