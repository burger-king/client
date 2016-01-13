import os
import json
import click
import shutil
from bkpm.cli import excs, util, api

config_path = os.path.expanduser('~/.bkrc')


def _get_meta_data():
    cwd = os.getcwd()
    try:
        meta_data = json.load(open(os.path.join(cwd, 'meta.json'), 'r'))
    except IOError:
        click.echo('The models\' metadata must be specified in "meta.json"')
    return meta_data


def _get_model_data():
    cwd = os.getcwd()
    try:
        model_data = json.load(open(os.path.join(cwd, 'model.json'), 'r'))
    except IOError:
        click.echo('The models\' model data must be specified in "model.json"')
    return model_data


def _get_latest_version(ctx, name):
    resp = ctx.obj['api'].get_meta(name)
    meta = resp.json()
    return meta['version']


def _parse_name(name):
    parts = name.split('@')
    if len(parts) == 1:
        parts.append('latest')
    name, version = parts
    return name, version


@click.group()
@click.option('--registry', '-r', default='default')
@click.pass_context
def cli(ctx, registry):
    """install and manage models"""
    config = util.load_config(config_path, registry)
    ctx.obj = {}
    ctx.obj['api'] = api.API(config['host'], config.get('token'))
    ctx.obj['models_dir'] = config.get('models_dir', os.path.expanduser('~/.models'))


@cli.command()
@click.argument('name')
@click.pass_context
def register(ctx, name):
    """register a model"""
    try:
        ctx.obj['api'].register(name)
        click.echo('Model "{}" was successfully registered'.format(name))
    except excs.MissingAuthException:
        click.echo('You must specify a token in your config ({}). Run the login command to get one.'.format(config_path))
    except excs.ModelConflictException:
        click.echo('There is already a model named "{}"'.format(name))


@cli.command()
@click.pass_context
def publish(ctx):
    """publish a model"""
    meta_data = _get_meta_data()
    model_data = _get_meta_data()
    name = meta_data['name']
    version = meta_data['version']
    try:
        ctx.obj['api'].publish(meta_data, model_data)
        click.echo('"{}" ({}) was successfully published'.format(name, version))
    except excs.MissingAuthException:
        click.echo('You must specify a token in your config ({}). Run the login command to get one.'.format(config_path))
    except excs.AuthenticationException:
        click.echo('You are not properly authenticated')
    except excs.ModelConflictException:
        version = _get_latest_version(ctx, name)
        click.echo('Version must be greater than {}'.format(version))


@cli.command()
@click.argument('name')
@click.pass_context
def install(ctx, name):
    """install a model"""
    name, version = _parse_name(name)
    if version == 'latest':
        version = _get_latest_version(ctx, name)
    model_path = os.path.join(ctx.obj['models_dir'], name)
    path = os.path.join(model_path, version)
    if os.path.isdir(path):
        click.echo('"{}" ({}) is already installed'.format(name, version))
    else:
        try:
            resp = ctx.obj['api'].get_archive(name, version)
            version = util.extract_model(resp.content, ctx.obj['models_dir'])
            click.echo('"{}" ({}) was successfully installed'.format(name, version))
        except excs.ModelNotFoundException:
            if version is 'latest':
                click.echo('No model "{}" was found'.format(name))
            else:
                click.echo('No model "{}" ({}) was found'.format(name, version))


@cli.command()
@click.argument('name')
@click.pass_context
def uninstall(ctx, name):
    """uninstall a model"""
    name, version = _parse_name(name)
    if version == 'latest':
        version = _get_latest_version(ctx, name)
    model_path = os.path.join(ctx.obj['models_dir'], name)
    path = os.path.join(model_path, version)
    if not os.path.isdir(path):
        if version is 'latest':
            click.echo('"{}" is not installed'.format(name))
        else:
            click.echo('"{}" ({}) is not installed'.format(name, version))
    else:
        shutil.rmtree(path)
        if not os.listdir(model_path):
            os.rmdir(model_path)
        click.echo('"{}" ({}) was successfully uninstalled'.format(name, version))


@cli.command()
@click.argument('name')
@click.pass_context
def unregister(ctx, name):
    """unregister a model"""
    name, version = _parse_name(name)
    try:
        ctx.obj['api'].delete(name, version)
        if version is 'all':
            click.echo('Version {} of "{}" was successfully deleted'.format(version, name))
        else:
            click.echo('"{}" was successfully deleted'.format(name))
    except excs.ModelNotFoundException:
        if version is 'all':
            click.echo('No model "{}" was found'.format(name))
        else:
            click.echo('No version {} of "{}" was found'.format(version, name))
    except excs.MissingAuthException:
        click.echo('You must specify a token in your config ({}). Run the login command to get one.'.format(config_path))
    except excs.AuthenticationException:
        click.echo('Models can only be managed by their owners')


@cli.command()
@click.argument('query')
@click.pass_context
def search(ctx, query):
    """search through models"""
    resp = ctx.obj['api'].search(query)
    results = resp.json()['results']
    if not results:
        click.echo('No results for "{}"'.format(query))
    else:
        for result in results:
            desc = result['description']
            vers = result['version']
            if desc is None:
                desc = 'No description provided.'
            click.echo('{} ({}) --> {}'.format(
                result['name'],
                vers if vers is not None else 'none',
                (desc[:78] + '..') if len(desc) > 80 else desc))


@cli.command()
@click.pass_context
def signup(ctx):
    """signup as a new user"""
    signup_url = '{}/users/signup'.format(ctx.obj['api'].host)
    click.launch(signup_url)
    click.echo('You can login via the `login` command')


@cli.command()
@click.pass_context
def login(ctx):
    """login/authenticate"""
    login_url = '{}/users/login'.format(ctx.obj['api'].host)
    click.launch(login_url)
    token = input('Enter your token: ')
    util.save_config(config_path, registry='default', token=token)