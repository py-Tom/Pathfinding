"""
GUI connected to path-finding algorithms.

GUI can be used for setting start point, end point and obstacles.
May run algorithm with option for demonstrating principles of operation.
"""


from tkinter import Tk, Canvas, PhotoImage, StringVar
from tkinter.ttk import Style, Frame, Label, Entry, Button, Radiobutton, Combobox, Checkbutton
from astar_algorithm import to_coord

GRID_WIDTH = 800
GRID_HEIGHT = 800
MAX_ENTRY = 100
COLOR_BACK = '#99D9EA'
COLOR_GRID = '#99CCFF'
COLOR_OUTLINE = '#FFFFFF'
COLOR_START = '#00FF00'
COLOR_END = '#338844'
COLOR_WALL = '#898989'
cell_id = {}


class Cell:
    """Create cells that will be drawn on canvas."""

    def __init__(self, x, y, size):
        """Set coordinates and size of each cell."""
        self.name = f'x{x}y{y}'
        self.size = size
        self.coord_x = x * size
        self.coord_y = y * size
        self.coord_x2 = self.coord_x + self.size
        self.coord_y2 = self.coord_y + self.size
        self.coord = (x, y)


def onclick(event):
    """Change colors and tags of cells according to user's input"""
    try:
        rv = radio_value.get()
        rb = radio_brush.get()
        current_tag = cell_id[f'x{event.x // size_of_cell}y{event.y // size_of_cell}']
        # change adjacent cells depending of cursor size
        if rb == 'medium':  # 4 squares
            if (current_tag / number_of_cells).is_integer():  # if cursor on bottom
                brush_tags = [current_tag, current_tag + number_of_cells]
            else:
                brush_tags = [current_tag, current_tag + 1, current_tag + number_of_cells,
                              current_tag + 1 + number_of_cells]
        elif rb == 'big':  # 9 squares
            if ((current_tag - 1) / number_of_cells).is_integer():  # if cursor on top
                brush_tags = [current_tag, current_tag + 1, current_tag + number_of_cells,
                              current_tag + 1 + number_of_cells, current_tag - number_of_cells,
                              current_tag + 1 - number_of_cells]
            elif (current_tag / number_of_cells).is_integer():  # if cursor on bottom
                brush_tags = [current_tag, current_tag + number_of_cells, current_tag - 1,
                              current_tag - number_of_cells,
                              current_tag - 1 + number_of_cells, current_tag - 1 - number_of_cells]
            else:
                brush_tags = [current_tag, current_tag + 1, current_tag + number_of_cells,
                              current_tag + 1 + number_of_cells, current_tag - 1, current_tag - number_of_cells,
                              current_tag - 1 + number_of_cells, current_tag - 1 - number_of_cells,
                              current_tag + 1 - number_of_cells]
        else:
            brush_tags = [current_tag]  # 1 square

        # can only set one start and end point
        if rv == 'start':
            if not can_cells.find_withtag("start"):
                can_cells.itemconfig(current_tag, fill=COLOR_START, tags=('cells', 'start'))
        elif rv == 'end':
            if not can_cells.find_withtag("end"):
                can_cells.itemconfig(current_tag, fill=COLOR_END, tags=('cells', 'end'))
        elif rv == 'wall':
            for tags in brush_tags:
                can_cells.itemconfig(tags, fill=COLOR_WALL, tags=('cells', 'wall'))
        elif rv == 'del':
            for tags in brush_tags:
                can_cells.itemconfig(tags, fill=COLOR_GRID, tags=('cells', 'normal', cell_id_reversed[tags]))

    except (IndexError, KeyError):
        pass
    return None


def create_cells():
    """Draw rectangles representing cells on canvas"""

    global can_cells
    global cell_id_reversed
    for widget in main_frame.winfo_children():
        widget.destroy()  # destroy old canvas

    try:
        # set outline of rectangle depending of its size
        if size_of_cell >= 40:
            size_border_cell = 4
        elif size_of_cell >= 7:
            size_border_cell = 1
        else:
            size_border_cell = 0

        # border - 1 to create nice outline of canvas
        can_cells = Canvas(main_frame, width=number_of_cells * size_of_cell - size_border_cell - 1,
                           height=number_of_cells * size_of_cell - size_border_cell - 1, background=COLOR_GRID)
        can_cells.pack(anchor='center')
        cell_objlist = []

        for i in range(number_of_cells):
            for j in range(number_of_cells):
                cell_objlist.append(Cell(i, j, size_of_cell))

        for cell in cell_objlist:
            cell_id[cell.name] = can_cells.create_rectangle(cell.coord_x, cell.coord_y, cell.coord_x2, cell.coord_y2,
                                                            fill=COLOR_GRID, outline=COLOR_OUTLINE,
                                                            tags=('cells', 'normal', cell.name), width=size_border_cell)
        cell_id_reversed = {v: k for k, v in cell_id.items()}
        # binding allows color change according to user's input
        can_cells.tag_bind('cells', '<B1-Motion>', onclick)
        can_cells.tag_bind('cells', '<Button-1>', onclick)
    except NameError:
        pass
    return None


def check_entries(a, b, c):
    """Update label and entry widgets right after input"""
    # print(a, b, c)
    global number_of_cells
    global size_of_cell
    try:
        number_of_cells = int(entry_num_cells.get())
        size_of_cell = GRID_WIDTH // number_of_cells
        label_size_cells.config(text=size_of_cell)
        label_box_cells_var.set('\N{MULTIPLICATION SIGN}  'f' {number_of_cells} = {number_of_cells * number_of_cells}')
    except (ValueError, ZeroDivisionError):
        pass
    return None


def test_val(ins, value, size):
    """Limit input for entry widget"""
    if ins == '1':  # insert
        if not value.isdigit():  # is digit
            return False
        if int(size) > 2:  # maximum characters 3
            return False
        if int(value) > MAX_ENTRY:  # value less than max
            return False
    return True


def clean_output():
    """Clears output from last run."""
    for i in can_cells.find_withtag("normal"):
        can_cells.itemconfig(cell_id_reversed[i], fill=COLOR_GRID)


def run_algorithm():
    """Create reversed dictionary - name:ID and run algorithm's module."""
    start_id = can_cells.find_withtag("start")
    end_id = can_cells.find_withtag("end")
    wall_id = can_cells.find_withtag("wall")
    normal_id = can_cells.find_withtag("normal")
    start_coord = []
    end_coord = []
    wall_coord = []
    normal_coord = []
    for index_s in start_id:
        start_coord.append(cell_id_reversed[index_s])
    for index_e in end_id:
        end_coord.append(cell_id_reversed[index_e])
    for index_w in wall_id:
        wall_coord.append(cell_id_reversed[index_w])
    for index_n in normal_id:
        normal_coord.append(cell_id_reversed[index_n])

    draw_flag = True if drawing_var.get() == '1' else False  # str to bool
    # run function in algorithm module
    to_coord(start_coord, end_coord, wall_coord, normal_coord, number_of_cells, can_cells, draw_flag)
    return None


root = Tk()

# style configuration
s = Style()
s.theme_use('clam')
s.configure('mybuttons.TButton', padding=(5,0))
s.configure('main_frame.TFrame', background=COLOR_BACK)
s.configure('options.TFrame', background='#DCDAD5', relief='groove')

# basic frames separating options menu and grid
master_frame = Frame(root)
options_frame = Frame(master_frame, width=GRID_WIDTH, height=100)
main_frame = Frame(master_frame, width=GRID_WIDTH, height=GRID_HEIGHT, style='main_frame.TFrame')
master_frame.grid(row=0, column=0)
options_frame.grid(row=0, column=0, sticky='nswe')
main_frame.grid(row=1, column=0, sticky='nswe')

# set background image:
background_image = PhotoImage(file="images/background1.png")
background_label = Label(main_frame, image=background_image)
background_label.image = background_image
background_label.pack()

# center app window after resizing
master_frame.grid_rowconfigure(0, weight=1)
master_frame.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# setting options in option_frame
entry_num_cells_var = StringVar()
entry_num_cells_var.trace('w', check_entries)
label_box_cells_var = StringVar()
label_box_cells_var.set('\N{MULTIPLICATION SIGN}'f'       =')

radio_value = StringVar()
radio_value.set('start')
radio_brush = StringVar()
radio_brush.set('small')

algorithm_var = StringVar()
list_of_algorithms = ['A* A-Star']
algorithm_var.set(list_of_algorithms[0])
drawing_var = StringVar()
drawing_var.set(0)

# setting widgets in options frame
cell_options_frame = Frame(options_frame, style='options.TFrame', borderwidth=5)
text_cell_options = Label(cell_options_frame, text='Cell configuration')
text_num_cells = Label(cell_options_frame, text=f'row \N{MULTIPLICATION SIGN} col [max={MAX_ENTRY}]')
label_box_cells = Label(cell_options_frame, textvariable=label_box_cells_var)
entry_num_cells = Entry(cell_options_frame, textvariable=entry_num_cells_var, justify='right', width=3, validate="key")
entry_num_cells.configure(validatecommand=(entry_num_cells.register(test_val), '%d', '%P', '%i'))
text_size_cells = Label(cell_options_frame, text='size')
label_size_cells = Label(cell_options_frame, text='')
button_clear = Button(cell_options_frame, text='CLEAR', command=lambda: clean_output(), style='mybuttons.TButton')
button_update = Button(cell_options_frame, text='NEW', command=lambda: create_cells(), style='mybuttons.TButton')

radio_frame = Frame(options_frame, style='options.TFrame', borderwidth=5)
text_painting_options = Label(radio_frame, text='Drawing options')
radio_start = Radiobutton(radio_frame, text="START", variable=radio_value, value='start')
radio_end = Radiobutton(radio_frame, text="END", variable=radio_value, value='end')
radio_wall = Radiobutton(radio_frame, text="WALL", variable=radio_value, value='wall')
radio_del = Radiobutton(radio_frame, text="DEL", variable=radio_value, value='del')

brush_frame = Frame(options_frame, style='options.TFrame', borderwidth=5)
text_brush_options = Label(brush_frame, text='Cursor size')
radio_brush_small = Radiobutton(brush_frame, text='S', variable=radio_brush, value='small')
radio_brush_medium = Radiobutton(brush_frame, text='M', variable=radio_brush, value='medium')
radio_brush_big = Radiobutton(brush_frame, text='B', variable=radio_brush, value='big')

pre_run_frame = Frame(options_frame, style='options.TFrame', borderwidth=5)
text_pre_run = Label(pre_run_frame, text='Run settings')
combo_algorithms = Combobox(pre_run_frame, textvariable=algorithm_var, values=list_of_algorithms)
check_drawing = Checkbutton(pre_run_frame, text='draw during operation', variable=drawing_var)
button_run = Button(pre_run_frame, text='RUN', command=lambda: run_algorithm())

# positioning in options frame
cell_options_frame.grid(row=0, column=0, sticky='nswe')
cell_options_frame.grid_columnconfigure(1, minsize=84)
text_cell_options.grid(row=0, column=0, columnspan=4, pady=(0, 10))
text_num_cells.grid(row=1, column=0, columnspan=2, sticky='nswe', padx=10)
entry_num_cells.grid(row=2, column=0, sticky='w', padx=(10, 0))
label_box_cells.grid(row=2, column=1, sticky='w', padx=0)
text_size_cells.grid(row=1, column=2, padx=8)
label_size_cells.grid(row=2, column=2, padx=8)
button_clear.grid(row=1, column=3, padx=10, sticky='nswe')
button_update.grid(row=2, column=3, padx=10, sticky='nswe')

radio_frame.grid(row=0, column=1, sticky='nswe')
text_painting_options.grid(row=0, column=0, columnspan=2, pady=(0, 10))
radio_start.grid(row=1, column=0, padx=(10, 0), sticky='nswe')
radio_end.grid(row=1, column=1, padx=(0, 10), sticky='nswe')
radio_wall.grid(row=2, column=0, padx=(10, 0), sticky='nswe')
radio_del.grid(row=2, column=1, padx=(0, 10), sticky='nswe')

brush_frame.grid(row=0, column=2, sticky='nswe')
text_brush_options.grid(row=0, column=0, columnspan=3, pady=(0, 10))
radio_brush_small.grid(row=1, column=0, pady=10, padx=(10, 0), sticky='nswe')
radio_brush_medium.grid(row=1, column=1, pady=10, sticky='nswe')
radio_brush_big.grid(row=1, column=2, pady=10, padx=(0, 10), sticky='nswe')

pre_run_frame.grid(row=0, column=3, rowspan=2, sticky='nswe')
text_pre_run.grid(row=0, column=0, columnspan=2, pady=(0, 10))
check_drawing.grid(row=1, column=0, sticky='nswe', padx=10)
combo_algorithms.grid(row=2, column=0, sticky='nswe', padx=10)
button_run.grid(row=1, column=1, rowspan=2, sticky='nswe', padx=(12, 10))

root.mainloop()
