import io
from _ast import Expression
from contextlib import contextmanager
from textwrap import dedent


class Pyw:
    def __init__(self):
        self.io = io.StringIO()
        self.indent = 0

    @contextmanager
    def scope(self, start=None, end=None, pad=True):
        if start:
            self.write_line(start)
        old_indent = self.indent
        self.indent += 1
        yield
        self.indent -= 1
        if self.indent != old_indent:
            raise ValueError('misuse of scope()')
        if end:
            self.write_line(end)
        if pad:
            self.write_line('')

    def kwfunc(self, name, parameters):
        if parameters:
            return self.scope('def %s(self, *, %s):' % (name, ', '.join(parameters)))
        else:
            return self.scope('def %s(self):' % (name))

    def write_line(self, line=None):
        if not line:
            self.io.write('\n')
        else:
            self.io.write('%s%s\n' % ('    ' * self.indent, line))
        return self

    def write_block(self, block, pad=True):
        for line in dedent(block).splitlines():
            self.write_line(line)
        if pad:
            self.write_line()
        return self

    def write_func_call(self, retval, func, kwargs):
        if kwargs:
            with self.scope('%s = %s(' % (retval, func), end=')', pad=False):
                for key, value in kwargs.items():
                    if value is None:
                        continue
                    if isinstance(value, Expression):
                        self.write_line('%s=%s,' % (key, value.body))
                    else:
                        self.write_line('%s=%r,' % (key, value))
        else:
            self.write_line('%s = %s()' % (retval, func))

    def write_comment(self, comment, pad=False):
        for line in dedent(comment).splitlines():
            self.write_line('# %s' % line)
        if pad:
            self.write_line()
        return self
