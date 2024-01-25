from typing import Optional

from SPARQLWrapper import SPARQLWrapper, POST, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed

from marie.exceptions import KgConnectionError, QueryBadFormedError


class KgClient:
    QUERY_PREFIXES = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX ocape: <http://www.theworldavatar.com/ontology/ontocape/material/substance/reaction_mechanism.owl#>
PREFIX op: <http://www.theworldavatar.com/ontology/ontoprovenance/OntoProvenance.owl#>
PREFIX os: <http://www.theworldavatar.com/ontology/ontospecies/OntoSpecies.owl#>
PREFIX okin: <http://www.theworldavatar.com/ontology/ontokin/OntoKin.owl#>
PREFIX occ: <http://www.theworldavatar.com/ontology/ontocompchem/OntoCompChem.owl#>"""

    def __init__(
        self,
        kg_endpoint: str = "http://178.128.105.213:3838/blazegraph/namespace/ontospecies/sparql",
        user: Optional[str] = None,
        pw: Optional[str] = None,
    ):
        sparql = SPARQLWrapper(kg_endpoint)
        sparql.setReturnFormat(JSON)
        if user is not None and pw is not None:
            sparql.setCredentials(user=user, passwd=pw)
        sparql.setMethod(POST)
        self.sparql = sparql

    def query(self, query: str):
        """Queries the KG and returns the response with the following format
        {
            "head": {
                "vars": List[str]
            },
            "results": {
                "bindings": [
                    Dict[
                        str,
                        {
                            "datatype": NotRequired[str],
                            "type": str
                            "value" str
                        }
                    ]
                ]
            }
        }
        """
        if not query.startswith("PREFIX"):
            query = self.QUERY_PREFIXES + query

        self.sparql.setQuery(query)

        try:
            return self.sparql.queryAndConvert()
        except QueryBadFormed as e:
            raise QueryBadFormedError(e.args)
        except Exception:
            raise KgConnectionError()
