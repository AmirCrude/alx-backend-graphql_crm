import graphene
from crm.schema import Query, Mutation

class RootQuery(Query, graphene.ObjectType):
    hello = graphene.String()
    
    def resolve_hello(root, info):
        return "Hello, GraphQL!"

schema = graphene.Schema(query=RootQuery, mutation=Mutation)