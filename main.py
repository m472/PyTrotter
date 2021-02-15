from matplotlib import pyplot as plt
from geopy.geocoders import Nominatim
from random import sample
from cartopy import crs as ccrs
import cartopy.geodesic as gd
import cartopy
import matplotlib
matplotlib.use('tkagg')


class CallbackHandler:
    def __init__(self, fig, ax, correct_location, scores):
        self.fig = fig
        self.ax = ax
        self.correct_location = correct_location
        self.was_clicked = False
        self.scores = scores

    def onclick(self, event):
        if not self.was_clicked:
            self.ax.plot(event.xdata, event.ydata, 'bo')
            self.ax.plot(self.correct_location.longitude, self.correct_location.latitude, 'go',
                         transform=ccrs.Geodetic())

            coords = ccrs.PlateCarree().transform_point(event.xdata, event.ydata, self.ax.projection)
            correct_coords = (self.correct_location.longitude, self.correct_location.latitude)
            distance_km = gd.Geodesic().inverse(coords, correct_coords).base[0, 0] / 1000
            self.scores.append(distance_km)
            plt.title(f'Distance: {distance_km:.0f}km, Score: {sum(self.scores):.0f}')
            self.fig.canvas.draw()
            self.was_clicked = True
        else:
            plt.close()


with open('Capitals.txt') as f:
    cities = [line.strip() for line in f.readlines()]


geolocator = Nominatim(user_agent='globetr')
scores = []
for rnd in range(3):
    for city in sample(cities, 3):
        location = geolocator.geocode(city)

        fig = plt.figure()
        ax = plt.axes(projection=ccrs.Robinson())
        ax.set_global()

        if rnd == 0:
            ax.stock_img()
            ax.add_feature(cartopy.feature.BORDERS, edgecolor='black')
        elif rnd == 1:
            ax.add_feature(cartopy.feature.LAND, facecolor='black')
            ax.add_feature(cartopy.feature.BORDERS, edgecolor='white')
        else:
            ax.add_feature(cartopy.feature.LAND, facecolor='black')

        clickHandler = CallbackHandler(fig, ax, location, scores)
        fig.canvas.mpl_connect('button_press_event', clickHandler.onclick)
        ax.set_title(city)
        mng = plt.get_current_fig_manager()
        mng.frame.Maximize(True)
        scores = clickHandler.scores

plt.plot(scores, color='blue', marker='o', line='')
plt.title(f'Final Score: {sum(scores):.0f}')
plt.show()