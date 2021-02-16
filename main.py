from matplotlib import pyplot as plt
import matplotlib
from random import sample
from cartopy import crs as ccrs
import numpy as np
import geopy
import cartopy.geodesic as gd
import cartopy
import matplotlib
matplotlib.use('tkagg')


class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.scores = []
        self.guesses = []


class GameManager:
    def __init__(self, cities, player_names, num_rounds, num_levels, colors=None):
        self.num_levels = num_levels
        self.num_rounds = num_rounds

        if colors is None:
            cmap = matplotlib.cm.get_cmap('tab10')
            colors = [cmap(i) for i in range(len(player_names))]
        self.players = [Player(name, color) for name, color in zip(player_names, colors)]
        self.geolocator = geopy.geocoders.Nominatim(user_agent='pytrotter')
        self.cities = sample(cities, num_rounds * self.num_levels)
        self.locations = [self.geocode(city) for city in self.cities]

        self.fig = plt.figure()
        self.ax = plt.axes(projection=ccrs.Robinson())
        self.ax.set_global()
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.correct_location = None
        self.round = -1
        self.current_player_index = 0

    @property
    def current_player(self):
        return self.players[self.current_player_index % len(self.players)]

    def geocode(self, query):
        location = self.geolocator.geocode(query)
        if location is not None:
            return location
        else:
            raise Exception(f"Location for '{city}' not found")

    def start(self):
        self.next_round()
        plt.show()

    def draw_level(self, n):
        if n == 0:
            self.ax.stock_img()
            self.ax.add_feature(cartopy.feature.BORDERS, edgecolor='gray')
        elif n == 1:
            self.ax.add_feature(cartopy.feature.LAND, facecolor='black')
            self.ax.add_feature(cartopy.feature.BORDERS, edgecolor='white')
        else:
            self.ax.add_feature(cartopy.feature.LAND, facecolor='black')

    def next_round(self):
        plt.cla()
        self.round += 1
        if self.round < self.num_rounds * self.num_levels:
            self.correct_location = self.locations[self.round]
            level = self.round // self.num_rounds
            self.draw_level(level)
            self.set_ax_title()
            self.fig.canvas.draw()
        else:
            # End of Game
            plt.clf()

            ax = plt.axes()
            x = np.arange(len(self.cities))
            width = 0.7
            bar_width = width / len(self.players)
            scores = []
            for i, player in enumerate(self.players):
                ax.bar(x - width / 2 + bar_width / 2 + i * bar_width, player.scores, bar_width, color=player.color, label=player.name)
                scores.append(f'{player.name}: {sum(player.scores):.0f}')
            ax.set_title('Final Scores:\n' +  "\n".join(scores))
            ax.set_ylabel('Scores')
            ax.set_xticks(x)
            ax.set_xticklabels(self.cities)
            ax.legend()
            self.fig.canvas.draw()

    def set_ax_title(self):
            self.ax.set_title(f'Player {self.current_player.name}\nRound {self.round + 1}:   {self.cities[self.round]}')

    def onclick(self, event):
        if self.current_player_index < len(self.players):
            coords = ccrs.PlateCarree().transform_point(event.xdata, event.ydata, self.ax.projection)
            self.current_player.guesses.append(coords)

            self.ax.plot(event.xdata, event.ydata, marker='o', color=self.current_player.color)
            self.current_player_index += 1

            self.set_ax_title()
            self.ax.set_global()

            # check if this player was the last
            if self.current_player_index >= len(self.players):
                self.ax.set_global()
                result_strings = []
                for player in self.players:
                    self.ax.plot([player.guesses[-1][0], self.correct_location.longitude],
                                 [player.guesses[-1][1], self.correct_location.latitude],
                                 marker=None, color=player.color,
                                 transform=ccrs.Geodetic())
                    self.ax.plot(self.correct_location.longitude, 
                                 self.correct_location.latitude, 'g+',
                                 transform=ccrs.Geodetic())

                    correct_coords = (self.correct_location.longitude, self.correct_location.latitude)
                    distance_km = gd.Geodesic().inverse(player.guesses[-1], correct_coords).base[0, 0] / 1000
                    player.scores.append(distance_km)

                    # Get mouseclick location
                    try:
                        click_location_name = self.geolocator.reverse(player.guesses[-1][::-1], zoom=8, language='en')
                    except:
                        click_location_name = "Timeout"

                    result_strings.append(f'{player.name}: Distance = {player.scores[-1]:.0f} km, Score = {sum(player.scores):.0f}\nYou clicked at {click_location_name}')

                self.ax.set_title('\n\n'.join(result_strings))
            self.fig.canvas.draw()

        else:
            self.current_player_index = 0
            self.next_round()


if __name__ == '__main__':
    import argparse

    def level_type(s):
        i = int(s)
        if i > 3:
            raise argparse.ArgumentTypeError("Maximum number of levels is 3")
        return i

    parser = argparse.ArgumentParser("Location guessing game")
    parser.add_argument('--cities', default='Capitals.txt')
    parser.add_argument('--rounds', type=int, default=3, help='number of rounds per level and player')
    parser.add_argument('--levels', type=level_type, default=3, help='number levels')
    parser.add_argument('players', nargs='+', help='names of the players')
    args = parser.parse_args()

    with open(args.cities) as f:
        cities = [line.strip() for line in f.readlines() if not line.isspace()]

    game = GameManager(cities, args.players, args.rounds, args.levels)
    game.start()
