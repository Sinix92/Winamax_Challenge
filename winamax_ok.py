from cProfile import run as cProfile_run
from copy import deepcopy as copy_deepcopy
from random import shuffle as rd_shuffle
from math import factorial


def finalize_golf_course(golf_course):
    """
    :param golf_course: final golf course to clean
    :return: cleaned golf_course (without "BinH" and "X")
    """
    matrix_to_list = []
    for row in golf_course:
        for elt in row:
            if elt in {"X", "BinH"}:
                matrix_to_list.append(".")
            else:
                matrix_to_list.append(elt)
        matrix_to_list.append('\n')

    return ''.join(matrix_to_list)


def get_ball_directions(golf_course, ball, distance, directions_strategy, water_just_crossed, previous_direction):
    """
    :param golf_course: current state of golf course
    :param ball: current ball coordinates
    :param distance: distance the ball must respect on this shot
    :param directions_strategy: the order of the directions to respect
    :param water_just_crossed: True if the ball just crossed water
    :param previous_direction: direction that ball just followed
    :return: list of possible directions that ball will follow (avoid reverse direction)
    """
    dict_reverse_direction = {"v": "^", "^": "v", "<": ">", ">": "<"}
    ball_directions = []

    height = len(golf_course) - 1
    width = len(golf_course[0]) - 1

    # if ball just crossed water, it must follow the same direction as previously
    if water_just_crossed:
        if previous_direction == "v":
            if height - ball[0] >= distance:
                ball_directions.append(previous_direction)
        elif previous_direction == "^":
            if ball[0] >= distance:
                ball_directions.append(previous_direction)
        elif previous_direction == ">":
            if width - ball[1] >= distance:
                ball_directions.append(previous_direction)
        elif previous_direction == "<":
            if ball[1] >= distance:
                ball_directions.append(previous_direction)
    else:
        for direction in directions_strategy:
            if direction == "^":
                if ball[0] >= distance:
                    ball_directions.append("^")
            elif direction == ">":
                if width - ball[1] >= distance:
                    ball_directions.append(">")
            elif direction == "v":
                if height - ball[0] >= distance:
                    ball_directions.append("v")
            elif direction == "<":
                if ball[1] >= distance:
                    ball_directions.append("<")

    # Remove the reverse direction if it was selected
    if previous_direction and not water_just_crossed:
        if dict_reverse_direction[previous_direction] in ball_directions:
            ball_directions.remove(dict_reverse_direction[previous_direction])

    return ball_directions


def get_next_coord(ball, direction):
    """
    :param ball: current ball coordinates
    :param direction: direction that ball follows
    :return: ball coordinates after having passed the direction
    """
    if direction == "^":
        return ball[0] - 1, ball[1]
    elif direction == "v":
        return ball[0] + 1, ball[1]
    elif direction == "<":
        return ball[0], ball[1] - 1
    elif direction == ">":
        return ball[0], ball[1] + 1


def update_golf_course(golf_course, ball, distance, direction):
    """
    :param golf_course: current state of golf course
    :param ball: current ball coordinates
    :param distance: distance the ball must respect on this shot
    :param direction: direction that ball follows
    :return: golf course updated with current ball path drawn
    """
    # initialization of variables:
    water_just_crossed = False
    # need to copy the list because of backtracking (to be able to go back to the previous state of golf course)
    golf_course_to_update = copy_deepcopy(golf_course)

    # start ball
    golf_course_to_update[ball[0]][ball[1]] = direction
    ball = get_next_coord((ball[0], ball[1]), direction)

    # draws the path for the ball
    for i in range(1, distance):
        if golf_course_to_update[ball[0]][ball[1]] in {".", "X"}:
            golf_course_to_update[ball[0]][ball[1]] = direction
            ball = get_next_coord(ball, direction)
        # the ball passes through another hole or path: fail
        else:
            return False, None, None, None

    # checks where the ball just landed
    if golf_course_to_update[ball[0]][ball[1]] == "X":
        water_just_crossed = True
    # the ball lands on a hole already targeted or a path: fail
    elif golf_course_to_update[ball[0]][ball[1]] not in {".", "H"}:
        return False, None, None, None

    return True, water_just_crossed, golf_course_to_update, ball


def backtrack(golf_course, ball, distance, directions_strategy, water_just_crossed=False, previous_direction=None):
    """
    :param golf_course: current state of golf course
    :param ball: current ball coordinates
    :param distance: distance the ball must respect on this shot
    :param directions_strategy: the order of the directions to respect
    :param water_just_crossed: True if the ball just crossed water
    :param previous_direction: direction ball just followed
    :return: either the updated golf course if last direction the ball followed is a success, or None if it's a fail
    """
    # case ball is in the hole: success
    if golf_course[ball[0]][ball[1]] == "H":
        golf_course[ball[0]][ball[1]] = "BinH"  # BinH to warn the future path that this hole has been targeted
        return True, golf_course
    # case distance left is 0 and ball did not reach the hole: fail
    elif distance == 0:
        return False, None

    # ball_direction setup (list of possible directions)
    list_directions = get_ball_directions(golf_course, ball, distance, directions_strategy, water_just_crossed,
                                          previous_direction)

    for direction in list_directions:

        is_golf_course_updated, water_just_crossed, golf_course_updated, ball_updated = update_golf_course(golf_course,
                                                                                                           ball,
                                                                                                           distance,
                                                                                                           direction)
        # if golf_course_updated:
        #     print(finalize_golf_course(golf_course_updated))

        # if the direction the ball just followed is not a failure
        if is_golf_course_updated:
            # go further in the different paths the ball can still follow
            is_backtrack_ok, golf_course_updated = backtrack(golf_course_updated, ball_updated,
                                                             distance - 1, directions_strategy, water_just_crossed,
                                                             direction)
            # case the ball just hit the hole
            if is_backtrack_ok:
                return True, golf_course_updated
        # if the direction the ball just followed is a failure, try next direction
        else:
            continue

    # all directions have been a failure, no more possibility: fail
    return False, None


def find_another_order(list_to_shuffle, tuple_of_list, set_of_tuples):
    while tuple_of_list in set_of_tuples:
        rd_shuffle(list_to_shuffle)
        tuple_of_list = tuple(list_to_shuffle)
    set_of_tuples.add(tuple_of_list)


def get_possible_paths(golf_course, balls_distances, directions_strategy, set_balls_orders, set_directions_strategy):
    """
    :param golf_course: golf course (start status)
    :param balls_distances: list of the balls/distances to analyse
    :param directions_strategy: the order of the directions to respect
    :param set_balls_orders: set of all balls orders we tried for this directions strategy
    :param set_directions_strategy: set of all directions strategy we tried so far
    :return: golf course (final status)
    """
    # need to copy the list because of recursion (to be able to go back to the previous state of golf course)
    golf_course_updated = golf_course
    # Loop through the balls
    for ball_distance in balls_distances:
        ball = ball_distance[0]
        distance = ball_distance[1]
        # check a possible path by ball
        is_backtrack_ok, golf_course_updated = backtrack(golf_course_updated, ball, distance, directions_strategy)

        # if golf_course_updated:
        #     print(finalize_golf_course(golf_course_updated))

        # if the ball didn't find a path, it means that it's because
        # it has crossed another path or a hole already targeted
        if not is_backtrack_ok:
            # as long as we didn't try every possible ball order
            if len(set_balls_orders) < factorial(len(balls_distances)):
                # we push this ball_distance in front of the list (at the beginning)
                balls_distances.remove(ball_distance)
                balls_distances = [ball_distance] + balls_distances
                t_balls_distances = tuple(balls_distances)
                # we add this new order to the set of balls orders we already tried
                if t_balls_distances not in set_balls_orders:
                    set_balls_orders.add(t_balls_distances)
                # if after having tried all possible "ball to the front" strategy, we randomly shuffle the balls order
                else:
                    find_another_order(balls_distances, t_balls_distances, set_balls_orders)
            # if we tried every possible ball order, we alter the directions strategy
            else:
                set_balls_orders = set()
                set_balls_orders.add(tuple(balls_distances))
                find_another_order(directions_strategy, tuple(directions_strategy), set_directions_strategy)
            return get_possible_paths(golf_course, balls_distances, directions_strategy, set_balls_orders,
                                      set_directions_strategy)

    return golf_course_updated


#######################################################################
#######################################################################
#######################################################################

def main():
    golf_course = [
        ['.', '.', '.', 'X', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'X', 'X', '.', '.', '.', '.',
         '.', 'H', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'H', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.',
         '.', '.', 'H', '.', '.', '.'],
        ['.', 'X', 'X', 'X', 'X', 'X', '.', '.', '.', '.', '.', '.', '.', '.', 'X', 'X', 'X', 'X', 'X', '.', '.', 'X',
         'X', 'X', 'X', 'X', '.', '.', '.', '.', '.', 'X', 'X', 'X', 'X', 'X', '.', '.', '.', '.', '.', '.', '.', '.',
         'X', 'X', 'X', 'X', 'X', '.'],
        ['.', '.', '.', 'X', 'X', 'X', 'X', '.', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '.', '.', '.', '.', '.',
         '.', '.', '.', '.', 'X', '.', '.', '4', '.', '.', '.', '.', '.', '.', 'X', '.', '.', '4', '4', '.', '.', 'X',
         '.', '.', '.', '.', '.', '.'],
        ['.', '.', 'H', '5', 'X', 'X', '.', '.', '.', '.', '.', '.', '.', '.', 'X', 'X', '5', 'H', '.', '.', '.', '.',
         'H', '5', 'X', 'X', '.', '.', '.', '.', '.', '.', 'H', '5', 'X', 'X', '.', '.', '.', '.', '.', '.', '.', '.',
         'X', 'X', '5', 'X', '.', '.'],
        ['.', '.', '.', 'X', 'X', 'X', 'X', '.', '.', '.', '.', '.', '.', 'X', 'X', 'X', 'X', '.', '.', '.', '.', '.',
         '.', 'X', 'X', 'X', 'X', '.', '.', '.', '.', '.', '.', 'X', 'X', 'X', 'X', '.', '.', '.', '.', '.', '.', 'X',
         'X', 'X', 'X', 'X', 'X', 'X'],
        ['.', '.', '.', 'X', 'X', 'X', 'X', '.', '.', '.', '.', '.', '.', 'X', 'X', 'X', 'X', '.', '.', '.', '.', '.',
         '.', 'X', 'X', 'X', 'X', '.', '.', '.', '.', '.', '.', 'X', 'X', 'X', 'X', '.', '.', '.', '.', '.', '.', 'X',
         'X', 'X', 'X', '.', '.', 'X'],
        ['.', '.', '.', '.', 'X', 'X', '4', '.', '.', '.', '.', '.', '.', '4', 'X', 'X', '.', '.', '.', '.', '.', '.',
         '.', '.', 'X', 'X', '4', '.', '.', '.', '.', '.', '.', '.', 'X', 'X', '4', '.', '.', '.', '.', '.', '.', '4',
         'X', 'X', '.', '.', '.', 'X'],
        ['3', '.', '.', 'X', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'X', '.', '.', '3', '3', '.',
         '.', 'X', '.', '.', '.', '.', 'X', '.', '3', '.', '.', 'X', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.',
         '.', '.', 'X', '.', '.', 'X'],
        ['.', '.', '.', '.', 'X', 'X', 'X', 'X', 'X', '.', '.', 'X', 'X', 'X', 'X', 'X', '.', '.', '.', '.', '.', '.',
         '.', '.', 'X', 'X', 'X', 'X', 'X', '.', '.', '.', '.', '.', 'X', 'X', 'X', 'X', 'X', '.', '.', 'X', 'X', 'X',
         'X', 'X', '.', '.', '.', '.'],
        ['.', '.', '.', '.', 'H', '.', 'H', '.', '.', '.', '.', '.', '.', 'H', '.', 'H', '.', '.', '.', '.', '.', '.',
         '.', '.', 'H', '.', 'H', '.', '.', '.', '.', '.', '.', '.', 'H', '.', 'H', '.', '.', '.', '.', '.', '.', 'H',
         '.', 'H', '.', '.', '.', '.']]

    balls_distances = [((2, 29), 4), ((2, 39), 4), ((2, 40), 4), ((3, 3), 5), ((3, 16), 5), ((3, 23), 5), ((3, 33), 5),
                       ((3, 46), 5), ((6, 6), 4), ((6, 13), 4), ((6, 26), 4), ((6, 36), 4), ((6, 43), 4), ((7, 0), 3),
                       ((7, 19), 3), ((7, 20), 3), ((7, 30), 3)]
    set_balls_orders = set()
    set_balls_orders.add(tuple(balls_distances))
    directions_strategy = ["^", ">", "v", "<"]
    set_directions_strategy = set()
    set_directions_strategy.add(tuple(directions_strategy))

    ####### Calculate the number of possible paths #######
    nb_possibilities = 0
    for ball_distance in balls_distances:
        nb_possibilities += 4 * (1 if ball_distance[1] == 1 else 3 ** (ball_distance[1] - 1))
    print("Number of possibilities: {}".format(nb_possibilities))
    ######################################################

    # we get the final golf course
    final_golf_course = get_possible_paths(golf_course, balls_distances, directions_strategy, set_balls_orders,
                                           set_directions_strategy)

    # replace "BinH" and "X" by "."
    print(finalize_golf_course(final_golf_course))


if __name__ == "__main__":
    cProfile_run('main()')
    # main()
