__license__ = """
NML is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

NML is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with NML; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA."""

from nml import expression, generic, global_constants
from nml.ast import base_statement


class Member(base_statement.BaseStatement):
    def __init__(self, name, value):
        base_statement.BaseStatement.__init__(self, "structure-member", name.pos, False, False)
        self.name = name
        self.value = value

    def register_names(self):
        if not isinstance(self.name, expression.Identifier):
            raise generic.ScriptError("Member name should be an identifier.", self.name.pos)
        if self.name.value in global_constants.constant_numbers:
            raise generic.ScriptError("Member name shadows a global constant.", self.name.pos)
        global_constants.structures[self.name.value] = self.value.reduce(global_constants.const_list)

    def debug_print(self, indentation):
        generic.print_dbg(indentation, "Member")
        generic.print_dbg(indentation + 2, "Name:")
        self.name.debug_print(indentation + 4)

        generic.print_dbg(indentation + 2, "Value:")
        self.value.debug_print(indentation + 4)

    def get_action_list(self):
        return []

    def __str__(self):
        return "{} = {};".format(self.name, self.value)


class Initiator(base_statement.BaseStatementList):
    def __init__(self, statements, pos):
        base_statement.BaseStatementList.__init__(
            self, "structure-block", pos, base_statement.BaseStatementList.LIST_TYPE_NONE, statements, in_item=True
        )

    def debug_print(self, indentation):
        generic.print_dbg(indentation, "Initiator")
        base_statement.BaseStatementList.debug_print(self, indentation + 2)

    def __str__(self):
        res = "init {\n"
        for stmt in self.statements:
            res += "    " + str(stmt) + "\n"
        res += "}"
        return res


class Structure(base_statement.BaseStatementList):
    def __init__(self, pos, name, statements, initiator=None):
        base_statement.BaseStatementList.__init__(
            self, "structure-block", pos, base_statement.BaseStatementList.LIST_TYPE_NONE, statements, in_item=True
        )
        self.id = name
        if not initiator:
            initiator = Initiator([], pos)
        self.initiator = initiator
        self.const_list = None

    def register_names(self):
        tmp = global_constants.const_list
        global_constants.duplicate_storage_for_constants()
        self.const_list = global_constants.const_list
        self.initiator.register_names()
        base_statement.BaseStatementList.register_names(self)
        global_constants.load_old_const_list(tmp)
        global_constants.structures[self.id.value] = self

    def initiate(self, pos):
        return self

    def pre_process(self):
        base_statement.BaseStatementList.pre_process(self)

    def debug_print(self, indentation):
        generic.print_dbg(indentation, "Structure")
        self.id.debug_print(indentation + 2)
        self.initiator.debug_print(indentation + 2)
        base_statement.BaseStatementList.debug_print(self, indentation + 2)

    def __str__(self):
        res = "struct {} {{\n\n".format(self.id)
        res += str(self.initiator) + ""
        for stmt in self.statements:
            res += "\n\n" + str(stmt)
        res += "\n}"
        return res


class StructureCall(base_statement.BaseStatementList):
    def __init__(self, name, statements, pos):
        base_statement.BaseStatementList.__init__(
            self, "structure-init-call", pos, base_statement.BaseStatementList.LIST_TYPE_NONE, statements, in_item=True
        )
        self.name = name

    def debug_print(self, indentation):
        generic.print_dbg(indentation, "Structure Call")
        base_statement.BaseStatementList.debug_print(self, indentation + 2)

    def __str__(self):
        res = "{}::init (\n".format(self.name.value)
        for stmt in self.statements:
            res += "    " + str(stmt) + "\n"
        res += ");"
        return res
