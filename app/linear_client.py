import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LinearClient:
    """Client for interacting with Linear's GraphQL API."""
    
    API_URL = "https://api.linear.app/graphql"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }
    
    def _execute_query(self, query: str, variables: dict = None) -> dict:
        """Execute a GraphQL query against Linear's API."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(
            self.API_URL,
            json=payload,
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def get_teams(self) -> list:
        """Fetch all teams for configuration assistance."""
        query = """
        query {
            teams {
                nodes {
                    id
                    name
                    key
                }
            }
        }
        """
        result = self._execute_query(query)
        return result.get("data", {}).get("teams", {}).get("nodes", [])
    
    def get_projects(self, team_id: str) -> list:
        """Fetch projects for a team."""
        query = """
        query($teamId: String!) {
            team(id: $teamId) {
                projects {
                    nodes {
                        id
                        name
                    }
                }
            }
        }
        """
        result = self._execute_query(query, {"teamId": team_id})
        return result.get("data", {}).get("team", {}).get("projects", {}).get("nodes", [])
    
    def get_labels(self, team_id: str) -> list:
        """Fetch labels for a team."""
        query = """
        query($teamId: String!) {
            team(id: $teamId) {
                labels {
                    nodes {
                        id
                        name
                    }
                }
            }
        }
        """
        result = self._execute_query(query, {"teamId": team_id})
        return result.get("data", {}).get("team", {}).get("labels", {}).get("nodes", [])
    
    def create_issue(
        self,
        team_id: str,
        title: str,
        description: str,
        priority: int = 2,
        project_id: Optional[str] = None,
        label_ids: Optional[list] = None,
    ) -> dict:
        """Create a new issue in Linear."""
        mutation = """
        mutation IssueCreate($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    url
                }
            }
        }
        """
        
        input_data = {
            "teamId": team_id,
            "title": title,
            "description": description,
            "priority": priority,
        }
        
        if project_id:
            input_data["projectId"] = project_id
        
        if label_ids:
            input_data["labelIds"] = label_ids
        
        result = self._execute_query(mutation, {"input": input_data})
        
        if "errors" in result:
            logger.error(f"Linear API error: {result['errors']}")
            raise Exception(f"Failed to create issue: {result['errors']}")
        
        return result.get("data", {}).get("issueCreate", {})
    
    def find_existing_issue(self, team_id: str, finding_id: str) -> Optional[dict]:
        """Check if an issue already exists for this finding."""
        query = """
        query($filter: IssueFilter) {
            issues(filter: $filter) {
                nodes {
                    id
                    identifier
                    title
                    url
                }
            }
        }
        """
        
        # Search for issues containing the finding ID in description
        result = self._execute_query(query, {
            "filter": {
                "team": {"id": {"eq": team_id}},
                "description": {"contains": finding_id}
            }
        })
        
        nodes = result.get("data", {}).get("issues", {}).get("nodes", [])
        return nodes[0] if nodes else None
    
    def test_connection(self) -> bool:
        """Test the API connection."""
        try:
            self.get_teams()
            return True
        except Exception as e:
            logger.error(f"Linear connection test failed: {e}")
            return False

