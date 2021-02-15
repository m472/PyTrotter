from matplotlib import pyplot as plt
from geopy.geocoders import Nominatim
from random import sample
from cartopy import crs as ccrs
import cartopy.geodesic as gd
import cartopy
import matplotlib
matplotlib.use('tkagg')


class GameManager:
    def __init__(self, cities, num_rounds):
        self.num_levels = 3
        self.num_rounds = num_rounds
        self.cities = sample(cities, self.num_rounds * self.num_levels)

        geolocator = Nominatim(user_agent='globetr')
        self.locations = [geolocator.geocode(city) for city in self.cities]

        self.was_clicked = False
        self.scores = []

        self.fig = plt.figure()
        self.ax = plt.axes(projection=ccrs.Robinson())
        self.ax.set_global()
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.correct_location = None
        self.round = 0

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
        if self.round < len(self.cities):
            self.correct_location = self.locations[self.round]
            level = self.round // self.num_levels
            self.draw_level(level)
            self.ax.set_title(f'Round {self.round + 1}:   {self.cities[self.round]}')
            self.fig.canvas.draw()
            self.round += 1
        else:
            plt.close()
            print(self.scores)
            plt.plot(self.scores, color='blue', marker='o', linestyle='')
            plt.title(f'Final Score: {sum(self.scores):.0f}')

    def onclick(self, event):
        if not self.was_clicked:
            coords = ccrs.PlateCarree().transform_point(event.xdata, event.ydata, self.ax.projection)
            self.ax.set_global()
            self.ax.plot([coords[0], self.correct_location.longitude],
                         [coords[1], self.correct_location.latitude],
                         'r-',
                         transform=ccrs.Geodetic())
            self.ax.plot(event.xdata, event.ydata, 'bo')
            self.ax.plot(self.correct_location.longitude, self.correct_location.latitude, 'go',
                         transform=ccrs.Geodetic())

            correct_coords = (self.correct_location.longitude, self.correct_location.latitude)
            distance_km = gd.Geodesic().inverse(coords, correct_coords).base[0, 0] / 1000
            self.scores.append(distance_km)
            self.ax.set_title(f'Distance: {distance_km:.0f} km, Score: {sum(self.scores):.0f}')
            self.fig.canvas.draw()
            self.was_clicked = True
        else:
            self.next_round()
            self.was_clicked = False


with open('Capitals.txt') as f:
    cities = [line.strip() for line in f.readlines()]

game = GameManager(cities, 3)
game.start()
