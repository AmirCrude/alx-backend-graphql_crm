import graphene

class Query(graphene.ObjectType):
    # a field called 'hello' that returns a String
    hello = graphene.String()

    # 'resolver' function provides the data for the 'hello' field
    def resolve_hello(root, info):
        return "Hello, GraphQL!"

# Create the schema instance
schema = graphene.Schema(query=Query)