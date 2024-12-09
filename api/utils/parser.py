from argparse import _SubParsersAction, ArgumentParser
import argparse
from datetime import datetime
from api import (
    DatabaseContext,
    get_global_database_context,
    get_global_user_token,
    set_global_database_context,
    set_global_user_token,
)
from utils.dict_utils import safe_pop
from utils.func_utils import get_callable_args, get_required_args
from utils.path_utils import is_valid_path, is_valid_dir
from utils.date_utils import parse_date
from utils.str_utils import str_to_bool
from inspect import signature

from utils.url_utils import is_valid_url


def parse_args_to_dict(args):
    args_dict = {}
    for i in range(1, len(args), 2):
        if i + 1 < len(args):
            key = args[i].lstrip("-")
            value = args[i + 1]
            # Convert 'true'/'false' to boolean
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            args_dict[key] = value
    return args_dict


class Argument:
    name = None
    type = str
    help = ""
    default = None
    choices: list = None
    nargs: int = None
    required: bool = None

    def __init__(
        self,
        name: str = None,
        type=str,
        default=None,
        help="",
        choices=None,
        nargs=None,
        required=None,
        action=None,
    ) -> None:
        self.name = self.get_name(name)
        self.type = type
        self.help = help
        self.default = default
        self.choices = choices
        self.nargs = nargs
        self.required = required
        self.action = action

    def get_name(self, name):
        if name is None:
            return None
        elif isinstance(name, str):
            return (name,)
        elif isinstance(name, tuple):
            return name
        else:
            raise ValueError("Invalid type for the 'name' argument")

    def get_arguments(args: list = []):
        arguments = [
            (
                Argument(**dict(zip(vars(Argument()).keys(), arg)))
                if not isinstance(arg, Argument)
                else arg
            )
            for arg in args
        ]
        return arguments

    def get_argument_dictionary(self):
        dictionary = self.__dict__.copy()
        safe_pop(dictionary, "name")

        name = self.name[0] if isinstance(self.name, tuple) else self.name

        if not (name.startswith("-")):
            safe_pop(dictionary, "required")

        if dictionary.get("action") and not (isinstance(self.action, argparse.Action)):
            safe_pop(dictionary, ["type", "nargs", "default"])

        return dictionary

    def __str__(self) -> str:
        return str(vars(self))


class StoreArgument(Argument):
    def __init__(self, name: str = ("--parameters"), action="store_true") -> None:
        super().__init__(name, action=action)


class DateArgument(Argument):
    def __init__(
        self,
        name: str = ("-d", "--date_created"),
        help="Specify date",
        default=None,
        type=parse_date,
    ) -> None:
        super().__init__(name, help=help, default=default, type=type)


class PathArgument(Argument):
    def __init__(
        self, name: str = ("-p", "--path"), type=is_valid_path, default=None, help=""
    ) -> None:
        super().__init__(name, type, help=help, default=default)


class DirectoryArgument(Argument):
    def __init__(
        self, name: str = "--directory", type=is_valid_dir, default=None, help=""
    ) -> None:
        super().__init__(name, type, help=help, default=default)


def is_valid_url_type(url: str):
    if is_valid_url(url):
        return url

    raise ValueError("Invalid url argument.")


class URLArgument(Argument):
    def __init__(
        self, name: str = ("-u", "--url"), type=is_valid_url_type, default=None, help=""
    ) -> None:
        super().__init__(name, type, default=default, help=help)


class BoolArgument(Argument):
    def __init__(
        self,
        name: str = "--is_checked",
        type=str_to_bool,
        default=False,
        help="",
        choices=[0, 1, "true", "false", True, False, None],
    ) -> None:
        super().__init__(name, type, help=help, default=default, choices=choices)


class SubCommand:
    subcommand_arguments: list[Argument]
    description: str = ""
    name: str = ""

    def __init__(
        self, name: str, subcommand_arguments: list = [], description=""
    ) -> None:
        self.name = name
        self.subcommand_arguments = Argument.get_arguments(subcommand_arguments)
        self.description = description

        if subcommand_arguments and not all(
            isinstance(argument, Argument) for argument in self.subcommand_arguments
        ):
            raise ValueError("arguments can only be of type Argument.")

    def create_subcommand(self, subparsers):

        # add parser to subparsers
        subcommand = subparsers.add_parser(self.name, description=self.description)
        for arg in self.subcommand_arguments:
            arg: Argument
            arg_dict = arg.get_argument_dictionary()
            # print(arg_dict)
            subcommand.add_argument(*arg.name, **arg_dict)

        return subcommand


class Parser:

    parser_arguments: list[Argument] = []
    subcommands: list[SubCommand] = []

    args = None

    def __init__(self, parser_arguments=[], subcommands=[]) -> None:
        self.parser = ArgumentParser()

        if parser_arguments:
            self.add_parser_arguments(parser_arguments)

        if subcommands:
            self.subparsers = self.parser.add_subparsers(
                title="Commands", dest="command"
            )
            self.create_subcommands(subcommands)

    def get_command_args(self):
        """
        Get parser arguments.
        """
        self.args = vars(self.parser.parse_args())

        cmd = self.args.get("command")

        if cmd:
            subcommand_arguments = next(
                subcommand.subcommand_arguments
                for subcommand in self.subcommands
                if subcommand.name == cmd
            )

            args = {}

            for arg in subcommand_arguments:
                arg: Argument
                arg_name = arg.name
                arg_name = arg_name[1] if len(arg.name) == 2 else arg_name[0]
                arg_name = arg_name.replace("-", "")
                args.update({arg_name: self.args.get(arg_name)})

            return args

        # create parser arguments dictionary
        safe_pop(self.args, "command")

        # remove all arguments that don't matter

        temp_dict = self.args.copy()
        for key, item in self.args.items():
            if item is None:
                temp_dict.pop(key)

        return temp_dict

    def add_parser_arguments(self, parser_arguments: list):
        """
        Adds parser arguments to ArgumentParser object.
        """

        if not all(
            isinstance(argument, Argument) for argument in self.parser_arguments
        ):
            raise ValueError("arguments can only be of type Argument.")

        self.parser_arguments = Argument.get_arguments(parser_arguments)

        for arg in self.parser_arguments:
            arg: Argument
            arg_dict = arg.get_argument_dictionary()

            self.parser.add_argument(*arg.name, **arg_dict)

    def get_command_function(self, cmd_dictionary: dict, dest: str = "command"):
        """
        Given a dictionary of command-function pairs, return the appropriate function.
        """

        if not isinstance(cmd_dictionary, dict):
            raise ValueError("'commands' is not a dictionary.")

        if not isinstance(self.args, dict):
            raise ValueError("'commands' is not a dictionary.")

        main_command = self.args.get(dest)
        func = cmd_dictionary.get(main_command)
        return func

    def get_callable_args(self, func):
        """Returns a dictionary of parser arguments within a given function."""

        func_signature = signature(func)
        param_values = {
            param.name: param for param in func_signature.parameters.values()
        }
        args = {}

        cmd_args = self.get_command_args()

        for key, param in param_values.items():
            # check if required
            if key in cmd_args:
                args.update({key: cmd_args.get(key)})
            elif param.default == param.empty and param.name != "self":
                args.update({key: None})
        return args

    def create_subcommands(self, subcommands: list):
        """
        Creates a list of subparser commands.
        """

        if not all(isinstance(subparser, SubCommand) for subparser in subcommands):
            raise ValueError("subparsers can only be of type Subparser.")

        self.subcommands = subcommands

        for subcommand in self.subcommands:
            subcommand: SubCommand
            subcommand.create_subcommand(self.subparsers)

    def get_object_args(self, obj: object):
        args = self.get_command_args()

        for k, v in args.items():
            if hasattr(obj, k):
                setattr(obj, k, v)

        self.set_db(args)

        return args

    def set_db(self, args: dict):
        """
        Configure the database context and user token based on provided arguments.
        """
        db_context = args.get("database_context") or (
            DatabaseContext.SERVER if args.get("token") else None
        )
        token = args.get("token")

        if args.get("username") and args.get("password"):
            from models.user import User

            token = User(username=args["username"], password=args["password"]).login()
            db_context = DatabaseContext.SERVER

        set_global_database_context(db_context)
        set_global_user_token(token)


base_arguments = [
    Argument(
        name=("-db", "--database_context"),
        type=DatabaseContext,
        choices=[DatabaseContext.LOCAL, DatabaseContext.SERVER, None],
        default=None,
    ),
    Argument(name="--token", type=str, default=get_global_user_token()),
    Argument(name="--username", type=str),
    Argument(name="--password", type=str),
]
