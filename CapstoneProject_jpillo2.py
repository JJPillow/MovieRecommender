# Jennifer Pillow pillje@hotmail.com
# This program makes movie recommendations based on viewer ratings
#
# Recommendation algorithm based on code by: Soham Das
# https://www.analyticsvidhya.com/blog/2020/11/create-your-own-movie-movie-recommendation-system/

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.neighbors import NearestNeighbors
from tkinter import *
from tkinter import ttk
from scipy.sparse import csr_matrix
from ttkwidgets.autocomplete import AutocompleteCombobox
import collections
import logging


logging.basicConfig(filename='project.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.INFO)

# Get data from csv files
try:
    movie_plots = pd.read_csv('movie_plots.csv')
except IOError as e:
    logging.exception("movie_plots.csv not found")
    sys.exit()
# print(movie_plots.head())

try:  
    movie_data = pd.read_csv('movie_data.csv')
except IOError as e:
    logging.exception("movie_data.csv not found")
    sys.exit()
# print(movie_data.head())

try:
    rating_data = pd.read_csv('rating_data.csv')
except IOError as e:
    logging.exception("rating_data.csv not found")
    sys.exit()   
# print(rating_data.head())

# Examine rating distributions
# rt_ax = rating_data['rating'].plot.hist(bins=6)

# create matrix of ratings using movieId as rows and userId as columns
rating_matrix = rating_data.pivot(index='movieId', columns='userId', values='rating').fillna(0)
# print(rating_matrix.head())

dataset = csr_matrix(rating_matrix.values)
rating_matrix.reset_index(inplace=True)

# print(rating_matrix)

fit_algo = NearestNeighbors(metric='cosine', algorithm='auto', n_neighbors=20, n_jobs=-1)
fit_algo.fit(dataset)


def get_recommendations(movie_name):
    rec_list_len = 10
    movie_idx = movie_data.index[movie_data['title'] == movie_name]
    distances, indices = fit_algo.kneighbors(dataset[movie_idx], n_neighbors=rec_list_len+1)
    movie_rec_index = (sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())),
                              key=lambda z: z[1])[:0:-1])
    rec_list = []
    for i in movie_rec_index:
        movie_indx = rating_matrix.iloc[i[0]]['movieId']
        indx = movie_data[movie_data['movieId'] == movie_indx].index
        if indx != movie_idx:
            rec_list.append({'RECOMMENDATIONS': movie_data.iloc[indx]['title'].values[0], 'Distance': i[1]})
    if len(rec_list) > 10:
        del rec_list[10:]
    df = pd.DataFrame(rec_list, index=range(1, rec_list_len+1))
    return df


def get_genres(movie_list):
    # get rows from movie list that match movies in df
    movies = movie_list['RECOMMENDATIONS'].to_list()

    # extract genres
    full_movie_data = movie_data[movie_data.title.isin(movies)]
    genres = full_movie_data['genres'].to_list()
    genre_data = []
    for movie in genres:
        g = movie.split("|")
        for i in g:
            genre_data.append(i)

    # aggregate counts
    num_count_by_genre = collections.Counter(genre_data)
    genres = num_count_by_genre.keys()
    counts = num_count_by_genre.values()
    dic = {'Genre': genres, 'Count': counts}
    genre_df = pd.DataFrame(dic)
    return genre_df


def get_movie_info(movie):
    movie_id = movie_data.movieId[movie_data['title'] == movie].values[0]
    movie_info = movie_plots.loc[movie_plots['movieId'] == movie_id]
    movie_info = movie_info.drop(columns=['tmdbId', 'imdb_id', 'movieId'])
    genres = movie_data.genres[movie_data['title'] == movie].values[0]
    genres = genres.replace("|", ", ")
    movie_info['genres'] = genres
    return movie_info


# Testing function results
# test_movie='G.I. Jane (1997)'
# test_result = get_recommendations(test_movie)
# print(test_result)
# print(get_genres(test_result))
# info_result = get_movie_info(test_movie)
# print(info_result)
# print(info_result['overview'].values[0])

# Start GUI
root = Tk()
root.title('Get Movie Recommendations')
w = 1250    # width for the Tk root
h = 695     # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth()   # width of the screen
hs = root.winfo_screenheight()  # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2) - 40      # offset for toolbar at bottom of window

# set the dimensions of the screen and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

# create a main frame
main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=1)

# create a canvas
my_canvas = Canvas(main_frame)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# add a scrollbar to canvas
my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
my_scrollbar.pack(side=RIGHT, fill=Y)

# configure the canvas
my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda f: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

# create another frame inside the canvas
second_frame = Frame(my_canvas)

# add that new frame to a window in the canvas
my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

button_bg = 'dodgerblue'
style = ttk.Style(second_frame)
style.theme_use("clam")

plt.rcdefaults()
rcParams.update({'figure.autolayout': True})
fig = plt.Figure(figsize=(6, 5), dpi=70)
ax = fig.add_subplot(111)
ax.set_xlabel('Number of Recommendations')
ax.set_title('Recommendations by Genre')
bar1 = FigureCanvasTkAgg(fig, second_frame)
bar1.get_tk_widget().grid(row=3, column=4, columnspan=2, rowspan=4, padx=5)


second_frame_bg = 'navy'
second_frame.config(bg=second_frame_bg)
button_font = ('Arial', 11, 'bold')
text_color = 'white'
style.configure("Treeview.Heading", background=button_bg, foreground=text_color, font=button_font)

rec_tree = ttk.Treeview(second_frame, selectmode="browse")
error_label = Label(second_frame, bg=second_frame_bg, font=button_font)

title_label = Label(second_frame, bg=second_frame_bg, font=button_font, text="Title: ", fg=text_color)
title_label.grid(row=8, column=0)
title_txt = Text(second_frame, height=1, width=75, font=12)
title_txt.grid(row=8, column=1, columnspan=2)

rel_date_label = Label(second_frame, bg=second_frame_bg, font=button_font, text="Release Date: ", fg=text_color)
rel_date_label.grid(row=9, column=0)
rel_date_txt = Text(second_frame, height=1, width=75, font=12)
rel_date_txt.grid(row=9, column=1, columnspan=2)

imdb_id_label = Label(second_frame, bg=second_frame_bg, font=button_font, text="IMDB ID: ", fg=text_color)
imdb_id_label.grid(row=10, column=0)
imdb_id_txt = Text(second_frame, height=1, width=75, font=12)
imdb_id_txt.grid(row=10, column=1, columnspan=2)

rt_label = Label(second_frame, bg=second_frame_bg, font=button_font, text="Runtime(min): ", fg=text_color)
rt_label.grid(row=11, column=0)
rt_txt = Text(second_frame, height=1, width=75, font=12)
rt_txt.grid(row=11, column=1, columnspan=2)

genre_label = Label(second_frame, bg=second_frame_bg, font=button_font, text="Genre(s): ", fg=text_color)
genre_label.grid(row=12, column=0)
genre_txt = Text(second_frame, height=1, width=75, font=12)
genre_txt.grid(row=12, column=1, columnspan=2)

ov_label = Label(second_frame, bg=second_frame_bg, font=button_font, text="Overview: ", fg=text_color)
ov_label.grid(row=13, column=0)

ov_text_box = Text(second_frame, height=4, width=75, font=12, wrap=WORD)
ov_text_box.grid(row=13, column=1, columnspan=2)

ov_sb = Scrollbar(second_frame, orient=VERTICAL)
ov_sb.grid(row=13, column=3, sticky=NS)

ov_text_box.config(yscrollcommand=ov_sb.set)
ov_sb.config(command=ov_text_box.yview)

movie_rec_txt = "Choose from the list of movies to get recommendations for similar movies."
movie_rec_label = Label(second_frame, text=movie_rec_txt, bg=second_frame_bg, font=button_font, fg=text_color)

movie_info_txt = "Select a movie from the recommendations above to get more info."
movie_info_label = Label(second_frame, text=movie_info_txt, bg=second_frame_bg, font=button_font, fg=text_color)

# row 0 title
title = Label(second_frame, text='Movie Recommendations')
title.config(font=('Arial', 20, 'bold'), bg=second_frame_bg, fg=text_color)
title.grid(row=0, column=0, columnspan=6, pady=20)

# row 1 movie_rec label
movie_rec_label.grid(row=1, column=1)

# row 2 combobox and search button
entry = AutocompleteCombobox(second_frame, width=50, font=('Times', 16), completevalues=movie_data['title'].to_list())
entry.grid(row=2, column=1, columnspan=1, sticky="w", padx=10)


def clear_info():
    # clear text boxes and error label
    movie_info_label.config(bg=second_frame_bg, fg=text_color)
    title_txt.delete("1.0", "end")
    rel_date_txt.delete("1.0", "end")
    imdb_id_txt.delete("1.0", "end")
    rt_txt.delete("1.0", "end")
    genre_txt.delete("1.0", "end")
    ov_text_box.delete("1.0", "end")


def get_movie():
    # clear tree and error label
    rec_tree.delete(*rec_tree.get_children())
    error_label.config(text="", bg=second_frame_bg)
    clear_info()
    # get recommendations and populate tree
    movie = entry.get()
    if movie in movie_data['title'].to_list():
        result = get_recommendations(movie)
        rec_tree["columns"] = list(result.columns)
        rec_tree["show"] = "headings"

        # loop through column list for headers
        for col in rec_tree["columns"]:
            rec_tree.heading(col, text=col)
            rec_tree.column(col, anchor=CENTER, width=rec_tree.winfo_width())

        # put data in results tree view
        result_rows = result.to_numpy().tolist()
        for row in result_rows:
            rec_tree.insert("", "end", values=row)

        # create genre plot
        genre_counts = get_genres(result)
        bar1 = FigureCanvasTkAgg(fig, second_frame)
        bar1.get_tk_widget().grid(row=3, column=4, columnspan=2, rowspan=4, padx=5)
        genre_counts.plot(kind='barh', ax=ax, legend=False)
        ax.set_yticklabels(genre_counts['Genre'])
    else:
        error_label.config(bg="yellow", text="Movie not found.  Please choose from list.")
    return


rec_button = Button(second_frame, text=' Get Recommendations ', command=get_movie, bg=button_bg, font=button_font,
                    fg=text_color)
rec_button.grid(row=4, column=1, sticky="ew", padx=5)

# row 3 error label
error_label.grid(row=3, column=1)

# row 5 recommendations tree view
rec_tree.grid(row=5, column=1, columnspan=1, sticky="nsew", pady=20)


def get_info():
    clear_info()
 
    # grab record number
    sel_movie = rec_tree.focus()
    
    # grab record values
    values = rec_tree.item(sel_movie, 'values')
    if len(values) > 0:
        sel_movie = values[0]
        m_info = get_movie_info(sel_movie)
        
        # insert info into text boxes
        title_txt.insert("1.0", m_info['title'].values[0])
        rel_date_txt.insert("1.0", m_info['release_date'].values[0])
        imdb_id_txt.insert("1.0", m_info['imdbId'].values[0])
        rt_txt.insert("1.0", m_info['runtime'].values[0])
        genre_txt.insert("1.0", m_info['genres'].values[0])
        ov_text_box.insert("1.0", m_info['overview'].values[0])
        
    else:
        movie_info_label.config(bg="yellow", fg='black')


# row 6 instructions label and get info button
movie_info_label.grid(row=6, column=1)

# row 7 get Info button
info_button = Button(second_frame, text=' Get Movie Info', command=get_info, bg=button_bg, font=button_font,
                     fg=text_color)
info_button.grid(row=7, column=1, pady=5)

# row 13 exit button
exit_button = Button(second_frame, text='Exit Application', command=root.destroy, bg=button_bg, font=button_font,
                     pady=5, fg=text_color)
exit_button.grid(row=13, column=4)

root.mainloop()
