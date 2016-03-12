#pylint: skip-file
from ruruki.graphs import Graph

# create a empty graph
graph = Graph()


# create some constraints to ensure uniqueness
graph.add_vertex_constraint("person", "name")
graph.add_vertex_constraint("book", "title")
graph.add_vertex_constraint("author", "fullname")
graph.add_vertex_constraint("category", "name")


# add in a couple books and their authors
# Note that I am duplicating the books title property as a name too. This is for ruruki-eye display
programming = graph.get_or_create_vertex("category", name="Programming")
operating_systems = graph.get_or_create_vertex("category", name="Operating Systems")


python_crash_course = graph.get_or_create_vertex("book", title="Python Crash Course")
graph.set_property(python_crash_course, name="Python Crash Course")
eric_matthes = graph.get_or_create_vertex("author", fullname="Eric Matthes", name="Eric", surname="Matthes")
graph.get_or_create_edge(python_crash_course, "CATEGORY", programming)
graph.get_or_create_edge(python_crash_course, "BY", eric_matthes)


python_pocket_ref = graph.get_or_create_vertex("book", title="Python Pocket Reference")
graph.set_property(python_pocket_ref, name="Python Pocket Reference")
mark_lutz = graph.get_or_create_vertex("author", fullname="Mark Lutz", name="Mark", surname="Lutz")
graph.get_or_create_edge(python_pocket_ref, "CATEGORY", programming)
graph.get_or_create_edge(python_pocket_ref, "BY", mark_lutz)


how_linux_works = graph.get_or_create_vertex("book", title="How Linux Works: What Every Superuser Should Know", edition="second")
graph.set_property(how_linux_works, name=how_linux_works.properties["title"])
brian_ward = graph.get_or_create_vertex("author", fullname="Brian Ward", name="Brian", surname="Ward")
graph.get_or_create_edge(how_linux_works, "CATEGORY", operating_systems)
graph.get_or_create_edge(how_linux_works, "BY", brian_ward)


linux_command_line = graph.get_or_create_vertex("book", title="The Linux Command Line: A Complete Introduction", edition="first")
graph.set_property(linux_command_line, name=linux_command_line.properties["title"])
william = graph.get_or_create_vertex("author", fullname="William E. Shotts Jr.", name="William", surname="Shotts")
graph.get_or_create_edge(linux_command_line, "CATEGORY", operating_systems)
graph.get_or_create_edge(linux_command_line, "BY", william)


# let add some customers and book out some books
john = graph.get_or_create_vertex("person", name="John", surname="Doe")
graph.get_or_create_edge(john, "READING", python_crash_course)
graph.get_or_create_edge(john, "INTEREST", programming)

jane = graph.get_or_create_vertex("person", name="Jane", surname="Doe")
graph.get_or_create_edge(jane, "LIKE", operating_systems)
graph.get_or_create_edge(jane, "MARRIED-TO", john)
graph.get_or_create_edge(jane, "READING", linux_command_line)
graph.get_or_create_edge(jane, "READING", python_pocket_ref)


print "People:"
print graph.get_vertices("person").all()

print "\nPython books:"
print graph.get_vertices("book", title__icontains="Python").all()

print "\nVertex with identity number 0:"
print repr(graph.get_vertex(0))

print "\nUnion of books with 'Reference' and 'Crash Course' in the title:"
print (graph.get_vertices("book", name__contains="Reference") | graph.get_vertices("book", title__contains="Crash Course")).all()


print "\nPython books with that do not contain 'Crash Course' in the title:"
print (graph.get_vertices("book", name__contains="Python") - graph.get_vertices("book", title__contains="Crash Course")).all()
