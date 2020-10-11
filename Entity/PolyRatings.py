# PolyRatings


class PolyRating:
    def __init__(self, id, avg_rating, num_ratings, professors_id):
        self.id = id
        self.avg_rating = avg_rating
        self.num_ratings = num_ratings
        self.professors_id = professors_id
        self.is_view = False
