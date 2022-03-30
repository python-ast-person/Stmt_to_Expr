from __future__ import print_function

import ast,astpp,importlib,ast2src

tree=ast.parse('''
import random
n = random.randint(1, 99)
guess = int(input("Enter an integer from 1 to 99: "))
#while n != guess:
print()
if guess < n:
    print( "guess is low")
    guess = int(input("Enter an integer from 1 to 99: "))
elif guess > n:
    print("guess is high")
    guess = int(input("Enter an integer from 1 to 99: "))
else:
    print("you guessed it!")
    #break
print()
''')

ast.Match=type('Match',(ast.AST,),{})

invalid_stmts=(ast.FunctionDef,
                     ast.AsyncFunctionDef,
                     ast.ClassDef,
                     ast.Return,
                     ast.Delete,
                     ast.AugAssign,
                     ast.AnnAssign,
                     ast.AsyncFor,
#                     ast.While,
                     ast.With,
                     ast.AsyncWith,
                     ast.Match,
                     ast.Try,
                     ast.ImportFrom,
                     ast.Global,
                     ast.Nonlocal,
                     ast.Continue,
                    )

def stmt_list_to_expr(stmt_list):
  expr_list=ast.List([],ast.Load())
  add_expr=lambda x:add_wrapped_expr(expr_list,x)
  for i in stmt_list:
    print(i)
    if isinstance(i,invalid_stmts):
      raise SyntaxError("Invalid statment please try again in a later version")
    elif isinstance(i,(
                       ast.NamedExpr,
                       ast.UnaryOp,
                       ast.BinOp,
                       ast.BoolOp,
                       ast.Compare,
                       ast.Call,
                       ast.keyword,
                       ast.IfExp,
                       ast.Attribute,)):
      i.lineno=1
      add_expr(i)
    elif isinstance(i,ast.Assign):
      add_expr(assign_expr(i))
    elif isinstance(i,ast.Import):
      add_expr(import_expr(i))
    elif isinstance(i,ast.If):
      add_expr(if_expr_wrapper(i))
    elif isinstance(i,ast.While):
      pass

  return expr_list


def assign_expr(assign_stmt):
  return ast.NamedExpr(
    assign_stmt.targets[0],
    assign_expr_(
      assign_stmt.targets[1:],
      assign_stmt.value))

def assign_expr_(targets,value):
  if len(targets)==0:
    return value
  return ast.NamedExpr(targets[0],assign_expr_(targets[1:],value))

def import_expr(import_stmt):
  expr=ast.List([],ast.Load())
  def call_import(name):
    return ast.Call(
      ast.Attribute(
        ast.Name("importlib",ctx=ast.Load()),
        attr="import",
        ctx=ast.Load()),
      args=[name],keywords=[] )
  for i in import_stmt.names:
    expr.elts.append(call_import(i.name))
  return expr

def if_expr_wrapper(if_stmt):
  return ast.IfExp(
    test=if_stmt.test,
    body=stmt_list_to_expr(if_stmt.body),
    orelse=stmt_list_to_expr(if_stmt.orelse))

def add_wrapped_expr(target,expr):
  target.elts.append(
    ast.BoolOp(ast.And(),[expr,ast.Constant(None)]))

def while_yield(condition):
  while result:=condition():
    yield result

astpp,importlib

code=stmt_list_to_expr(tree.body)

#astpp.pdp(code)
print()
print(code)
#execable_code=ast.Expression(body=ast.Call(
#  ast.Name(id="list",ctx=ast.Load()),
#  args=[code],
#  keywords=[],
#))
execable_code=ast.Module(
  body=[ast.Expr(code)],
  type_ignore=[])
print(type(code))
execable_code.lineno=1
execable_code.body[0].lineno=1
ast.fix_missing_locations(execable_code)

ast.unparse(code)

#exec(
#  compile(execable_code,'<ast>','exec'))