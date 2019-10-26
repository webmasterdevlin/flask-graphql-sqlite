from graphene import ObjectType, String, Schema, relay, Field, List, Int
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import Game, Player, Team

from sqlalchemy import or_


class PlayerObject(SQLAlchemyObjectType):
    class Meta:
        model = Player
        interfaces = (relay.Node,)


class TeamObject(SQLAlchemyObjectType):
    class Meta:
        model = Team
        interfaces = (relay.Node,)


class GameObject(SQLAlchemyObjectType):
    class Meta:
        model = Game
        interfaces = (relay.Node,)


class Query(ObjectType):
    node = relay.Node.Field()
    all_players = SQLAlchemyConnectionField(PlayerObject)
    all_teams = SQLAlchemyConnectionField(TeamObject)
    all_games = SQLAlchemyConnectionField(GameObject)
    # Get a specific player (expects player name)
    get_player = Field(PlayerObject, name=String())
    # Get a game (expects game id)
    get_game = Field(GameObject, id=Int())
    # Get all games a team has played (expects team id)
    get_team_games = Field(lambda: List(GameObject), team=Int())
    # Get all players who play a certain position (expects position name)
    get_position = Field(lambda: List(PlayerObject), position=String())

    # Resolve our queries
    def resolve_get_player(parent, info, name):
        query = PlayerObject.get_query(info)
        return query.filter(Player.name == name).first()

    def resolve_get_game(parent, info, id):
        query = GameObject.get_query(info)
        return query.filter(Game.id == id).first()

    def resolve_get_team_games(parent, info, team):
        query = GameObject.get_query(info)
        return query.filter(or_(Game.winner_id == team, Game.loser_id == team)).all()

    def resolve_get_position(parent, info, position):
        query = PlayerObject.get_query(info)
        return query.filter(Player.position == position).all()

schema = Schema(query=Query)
