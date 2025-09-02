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

from nml import expression, generic
from nml.actions import action2layout
from nml.ast import base_statement
from nml.expression.array import Array


class InArrayFor(base_statement.BaseStatement):
    def __init__(self, array, param, expressions, pos=None):
        base_statement.BaseStatement.__init__(self, "for", pos, False, False)
        self.array = array
        self.param = param
        self.expressions = expressions

    def __str__(self):
        expressions_string = ""
        for expression in self.expressions:
            expressions_string += str(self.expressions[0]) + ', '
        expressions_string = expressions_string[:-2]
        return "[{} for {} in {}]".format(
            expressions_string, self.param, self.array,
        )

    def reduce(self, id_dicts=None, unknown_id_fatal=True):
        self.array = self.array.reduce(id_dicts, unknown_id_fatal)
        out_list = []
        param_dict = {self.param.value : 0}
        id_dicts.append(param_dict)
        for value in self.array.values:
            param_dict[self.param.value] = value.value
            for expression in self.expressions:
                out_list.append(expression.reduce(id_dicts, unknown_id_fatal))
        id_dicts.remove(param_dict)
        return Array(out_list, self.pos)


class For(base_statement.BaseStatementList):
    def __init__(self, name, param_list, layout_sprite_list, pos=None):
        base_statement.BaseStatementList.__init__(self, "spritelayout", pos, False, False)
        self.initialize(name, None, len(param_list))
        self.param_list = param_list
        self.register_map = {}  # Set during action generation for easier referencing
        self.layout_sprite_list = layout_sprite_list

    # Do not reduce expressions here as they may contain variables
    # And the feature is not known yet
    def pre_process(self):
        # Check parameter names
        seen_names = set()
        for param in self.param_list:
            if not isinstance(param, expression.Identifier):
                raise generic.ScriptError("spritelayout parameter names must be identifiers.", param.pos)
            if param.value in seen_names:
                raise generic.ScriptError("Duplicate parameter name '{}' encountered.".format(param.value), param.pos)
            seen_names.add(param.value)
        # spritelayout_base_class.pre_process(self)

    def collect_references(self):
        return []

    def debug_print(self, indentation):
        generic.print_dbg(indentation, "Sprite layout:", self.name.value)
        generic.print_dbg(indentation + 2, "Parameters:")
        for param in self.param_list:
            param.debug_print(indentation + 4)
        generic.print_dbg(indentation + 2, "Sprites:")
        for layout_sprite in self.layout_sprite_list:
            layout_sprite.debug_print(indentation + 4)

    def __str__(self):
        params = "" if not self.param_list else "({})".format(", ".join(str(x) for x in self.param_list))
        return "spritelayout {}{} {{\n{}\n}}\n".format(
            str(self.name), params, "\n".join(str(x) for x in self.layout_sprite_list)
        )

    def get_action_list(self):
        action_list = []
        if self.prepare_act2_output():
            for feature in sorted(self.feature_set):
                if feature == 0x04:
                    continue
                action_list.extend(action2layout.get_layout_action2s(self, feature))
        return action_list
