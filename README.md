# Road Network GIS Application (avec kubernetes)

This repository contains a PostGIS-based geospatial database setup and a Helm chart for deploying a Flask application with an Nginx frontend (as a load balancer). 

The database is managed using Docker Compose, including PostGIS/pgRouting, PgBouncer for connection pooling, and a creator service to generate road network content. 
The Helm chart deploys a Flask API (on 2 nodes, but we can increase) and Nginx as a front-end/load balancer, suitable for serving geospatial queries.

This approach could be used for any others spatial applications.

## Repository Structure
- `docker-compose.yml`: Defines the PostGIS database stack (PostGIS, PgBouncer, creator).
- `postgis/`: Configuration files for PostGIS and PgBouncer:
  - `init.sql`: Initializes the `qc_routing` database with PostGIS and pgRouting extensions.
  - `postgresql.conf`: PostgreSQL settings optimized for a 4 GB RAM server.
  - `pgbouncer.ini`: PgBouncer configuration for connection pooling.
  - `userlist.txt`: PgBouncer authentication file.
- `creator/`: Python script (`create_network.py`) and Dockerfile to generate road network data.
- `data`: spatial data for the road network.
- `locust`: a Python file to test the approach.
- `flask/`: Configuration files for the flask api
  - `app/`: source code of the API
  - `helm/`: definition for the kubernetes
- `nginx/`: definition of the load balancer Nginx.
- `.env`: Environment variables for Docker Compose (not tracked in Git).

## Application Architecture
The application is deployed across a single server for the database and a Kubernetes cluster for the Flask application and Nginx load balancer. The architecture is as follows:

- **Database Server** (Single Node, 4 GB RAM, Debian):
  - **PostGIS Database**: A PostgreSQL database with PostGIS and pgRouting extensions, running in a Docker container (`postgis` service). It stores geospatial road network data in the `qc_routing` database and is exposed on port 5432.
  - **PgBouncer**: A connection pooler running in a Docker container (`pgbouncer` service), managing connections to PostGIS to optimize resource usage. Exposed on port 6432.
  - **Creator Service**: A Python script (`create_network.py`) in a Docker container (`creator` service) that populates the `qc_routing` database with road network data (e.g., from GeoJSON or shapefiles). Connects to PgBouncer for efficient database access.

- **Kubernetes Cluster**:
  - **Flask Application** (2 Nodes):
    - The Flask application, (create an image in docker registry) deployed via a Helm chart, runs on two Kubernetes nodes for redundancy and scalability.
    - It serves geospatial queries (e.g., road network analysis) by connecting to the PostGIS database through PgBouncer.
    - Each node runs a Flask pod, configured with a small resource footprint to ensure performance on modest hardware.
  - **Nginx Load Balancer** (1 Node):
    - An Nginx instance, deployed via a Helm chart, runs on a dedicated Kubernetes node.
    - Acts as a reverse proxy and load balancer, distributing incoming HTTP requests across the two Flask nodes.
    - Exposed via a Kubernetes Service (typically on port 80) and optionally an Ingress for external access.

This architecture ensures efficient database access (via PgBouncer), scalability for the Flask application (via Kubernetes), and reliable request handling (via Nginx), while being optimized for a low-memory server environment.

## Prerequisites
- **Docker** and **Docker Compose**: Install on your server ([Docker Install](https://docs.docker.com/engine/install/), [Compose Install](https://docs.docker.com/compose/install/)).
- **Helm**: For deploying the Flask/Nginx application ([Helm Install](https://helm.sh/docs/intro/install/)).
- **Kubernetes Cluster**: Required for Helm deployment (we used Vultr cloud provider).
- **Python 3.9+**: For local development of the creator service.
- **Server Specs**: Minimum 4 GB RAM, Debian/Ubuntu recommended.
- **Git**: To clone the repository.

## Database Setup (Docker Compose)
The database stack includes:
- **PostGIS**: PostgreSQL with PostGIS and pgRouting extensions, exposed on port 5432.
- **PgBouncer**: Connection pooler, exposed on port 6432.
- **Creator**: Python service to populate the `qc_routing` database with road network data.

### Configuration
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/voirinprof/gis_kubernetes_routing.git
   cd gis_kubernetes_routing
   ```

2. **Create `.env` File**:
   Create a `.env` file in the root directory:
   ```env
   POSTGRES_USER=admin
   POSTGRES_PASSWORD=admin_password
   POSTGRES_DB=qc_routing
   DB_HOST=db
   DB_USER=qc_user
   DB_PASSWORD=qc_password
   DB_NAME=qc_routing
   POOL_MODE=transaction
   MAX_CLIENT_CONN=50
   DEFAULT_POOL_SIZE=3
   ```
   - Replace `admin_password` with a secure password.
   - `qc_user` is used by the creator service and PgBouncer.

3. **Start the Database Stack**:
   ```bash
   docker-compose up -d
   ```
   This starts:
   - PostGIS (`postgis`) on `localhost:5432`.
   - PgBouncer (`pgbouncer`) on `localhost:6432`.
   - Creator (`creator`) to populate the `qc_routing` database.

### Configuration Details
- **PostGIS**:
  - Image: `postgis/postgis:15-3.4`
  - Users: `admin` (superuser), `qc_user` (database owner).
  - Database: `qc_routing` with PostGIS and pgRouting extensions.
  - Optimized for 4 GB RAM (`shared_buffers=256MB`, `max_connections=20`).
- **PgBouncer**:
  - Image: `edoburu/pgbouncer:v1.24.0-p1`
  - Connection limits: `max_client_conn=50`, `default_pool_size=3`, `max_db_connections=5`.
  - Authentication: `userlist.txt` with `admin` and `qc_user`.
- **Creator**:
  - Builds from `./creator/Dockerfile`.
  - Connects to PgBouncer (`postgresql://qc_user:qc_password@pgbouncer:5432/qc_routing`).
  - Generates geospatial data (e.g., from GeoJSON or shapefiles).

## Flask/Nginx Deployment (Helm)
The Helm chart in the `helm/` directory deploys a Flask application and Nginx reverse proxy to serve geospatial queries from the `qc_routing` database.

### Helm Chart Structure
- `flask/helm/`:
  - `Chart.yaml`: Defines the Helm chart metadata.
  - `values.yaml`: Configuration for Flask (e.g., replicas, service ports, database url).
  - `templates/`:
    - `deployment.yaml`: Flask application deployment.
    - `service.yaml`: Kubernetes service for Flask.
    - `ingress.yaml`: Ingress configuration.

- `nginx/`:
  - `Chart.yaml`: Defines the Helm chart metadata.
  - `values.yaml`: Configuration for Nginx (e.g., replicas, service ports).
  - `templates/`:
    - `deployment.yaml`: Application deployment.
    - `service.yaml`: Kubernetes service for Nginx.
    - `ingress.yaml`: Ingress configuration.
    - `configmap.yaml`: Nginx configuration (e.g., proxy URL).


### Deployment Steps

1. **Create an image of your flask app (e.g.: flask-routing:latest)**
   - build your image `docker build -t xxxxxx/flask-routing:latest .`
   - put a tag `docker tag xxxxxx/flask-routing:latest ewr.vultrcr.com/xxxxxx/flask-routing:latest`
   - push the image to registry `docker push ewr.vultrcr.com/xxxxxx/flask-routing:latest`

Your image will be available to deploy on any node of kubernetes.

You may need to log (from your local computer) to put the image in the remote repo (`docker login https://ewr.vultrcr.com/xxxxxx ... `).

2. **Create `kubeconfig.yaml` File** (provided by Vultr):
   - define a variable : `export KUBECONFIG=kubeconfig.yaml`
   - allows to manage the kubernetes nodes from your computer

3. **Set Up Kubernetes**:
   - Ensure `kubectl` is configured:
     ```bash
     kubectl cluster-info
     ```

4. **Install Helm Chart**:
   - Navigate to the Helm chart directory (flask and nginx)
   - Update `values.yaml` with your database connection details
   - Install the chart:
     ```bash
     helm install flask-routing .
     ```
     or
     ```bash
     helm install nginx-release .
     ```

5. **Access the Application**:
   - Get the service URL (use the public IP of the load balancer):
     ```bash
     curl http://<ip of load balancer>/
     ```

6. **Verify Deployment**:
   - Check pod status:
     ```bash
     kubectl get pods
     ```

### Test
- **Locust**:
  - You could use `locust` to test your application : `locust -f locustfile.py`

## Troubleshooting
- **Database Issues**:
  - Check logs:
    ```bash
    docker logs postgis
    docker logs pgbouncer
    docker logs creator
    ```
  - Verify PgBouncer connections:
    ```bash
    docker exec -it pgbouncer psql -h 127.0.0.1 -p 5432 -U qc_user -d pgbouncer -c 'SHOW POOLS'
    ```
  - Ensure `qc_user` and `admin` are defined in `userlist.txt`.
- **Helm Deployment**:
  - Check pod logs:
    ```bash
    kubectl logs -l app=flask-routing
    ```
  - Debug Helm issues:
    ```bash
    helm lint .
    helm template .
    ```
- **Resource Constraints**:
  - Monitor memory usage:
    ```bash
    docker stats
    free -m
    ```
  - Reduce `max_client_conn` or `default_pool_size` in `pgbouncer.ini` if memory is tight.

## Contributing
- Fork the repository and submit pull requests for improvements.
- Report issues or feature requests via GitHub Issues.

## License
This project is licensed under the MIT License. See `LICENSE` for details.