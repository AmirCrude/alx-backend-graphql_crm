import graphene
from crm.schema import CRMQuery, CRMMutation

class CRMQuery(graphene.ObjectType):
    pass

class Query(CRMQuery, graphene.ObjectType):
    hello = graphene.String()
    
    def resolve_hello(root, info):
        return "Hello, GraphQL!"

class Mutation(CRMMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)