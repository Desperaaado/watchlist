import click
from app import db, app
from app.models import User, Movie

@app.cli.command()
@click.option('--username', prompt=True, help="The username used to login.")
@click.option('--password', 
              prompt=True, 
              hide_input=True, 
              confirmation_prompt=True,
              help="The password used to login.")
@click.option('--nickname', prompt=True, help="Nickname.")
def admin(username, password, nickname):
    db.create_all()
    user = User.query.first()

    if not user:
        click.echo("Creating administrator...")
        user = User(user_name=username, name=nickname)
        user.set_password(password)
        user.user_name = username
        user.set_password(password)
        db.session.add(user)
    else:
        user.user_name = username
        user.name = nickname
        user.set_password(password)

    db.session.commit()
    click.echo("Done.")

@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:
        db.drop_all()
        click.echo('Drop data...\ndone.')
    db.create_all()
    click.echo('Initialized database.')

@app.cli.command()
def forge():
    db.create_all()

    name = 'Murphian Xiao'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)

    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Made data.')
