# A ball with a shotcount N will jump by N cells in one direction, vertically or horizontally.
# The shotcount is then decreased by 1 and the ball can jump again.

import itertools
import copy


def get_ball_directions(ball, hole, distance, golf_course, water_just_crossed, previous_direction):
    """
    :param ball: current ball coordinates
    :param hole: hole coordinates that ball targets
    :param distance: distance the ball respects on this shot
    :param golf_course: current state of golf course
    :param previous_direction: direction that ball just followed
    :param water_just_crossed: True if the ball just crossed water
    :return: list of possible directions that ball will follow (avoid reverse direction)
    """
    height = len(golf_course) - 1
    width = len(golf_course[0]) - 1

    dict_reverse_direction = {"v": "^", "^": "v", "<": ">", ">": "<"}
    ball_directions = []

    ############## ball must follow the previous direction ##############
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

    ############## ball to the top left of the hole ##############
    elif ball[0] < hole[0] and ball[1] < hole[1]:
        if height - ball[0] >= distance:
            ball_directions.append("v")  # first direction
        if width - ball[1] >= distance:
            ball_directions.append(">")  # second direction
        if ball[1] >= distance:
            ball_directions.append("<")  # third direction
        if ball[0] >= distance:
            ball_directions.append("^")  # fourth direction

    ############## ball right above the hole ##############
    elif ball[0] < hole[0] and ball[1] == hole[1]:
        if height - ball[0] >= distance:
            ball_directions.append("v")  # first direction
        if ball[1] >= distance:
            ball_directions.append("<")  # second direction
        if width - ball[1] >= distance:
            ball_directions.append(">")  # third direction
        if ball[0] >= distance:
            ball_directions.append("^")  # fourth direction

    ############## ball to the top right of the hole ##############
    elif ball[0] < hole[0] and ball[1] > hole[1]:
        if height - ball[0] >= distance:
            ball_directions.append("v")  # first direction
        if ball[1] >= distance:
            ball_directions.append("<")  # second direction
        if width - ball[1] >= distance:
            ball_directions.append(">")  # third direction
        if ball[0] >= distance:
            ball_directions.append("^")  # third/fourth direction

    ############## ball to the left of the hole ##############
    elif ball[0] == hole[0] and ball[1] < hole[1]:
        if width - ball[1] >= distance:
            ball_directions.append(">")  # first direction
        if ball[0] >= distance:
            ball_directions.append("^")  # second direction
        if height - ball[0] >= distance:
            ball_directions.append("v")  # second/third direction
        if ball[1] >= distance:
            ball_directions.append("<")  # second/third/fourth direction

    ############## ball to the right of the hole ##############
    elif ball[0] == hole[0] and ball[1] > hole[1]:
        if ball[1] >= distance:
            ball_directions.append("<")  # first direction
        if ball[0] >= distance:
            ball_directions.append("^")  # second direction
        if height - ball[0] >= distance:
            ball_directions.append("v")  # second/third direction
        if width - ball[1] >= distance:
            ball_directions.append(">")  # second/third/fourth direction

    ############## ball to the down left of the hole ##############
    elif ball[0] > hole[0] and ball[1] < hole[1]:
        if ball[0] >= distance:
            ball_directions.append("^")  # first direction
        if width - ball[1] >= distance:
            ball_directions.append(">")  # second direction
        if ball[1] >= distance:
            ball_directions.append("<")  # third direction
        if height - ball[0] >= distance:
            ball_directions.append("v")  # third/fourth direction

    ############## ball right below the hole ##############
    elif ball[0] > hole[0] and ball[1] == hole[1]:
        if ball[0] >= distance:
            ball_directions.append("^")  # first direction
        if ball[1] >= distance:
            ball_directions.append("<")  # second direction
        if width - ball[1] >= distance:
            ball_directions.append(">")  # second/third direction
        if height - ball[0] >= distance:
            ball_directions.append("v")  # second/third/fourth direction

    ############## ball to the down right of the hole ##############
    elif ball[0] > hole[0] and ball[1] > hole[1]:
        if ball[0] >= distance:
            ball_directions.append("^")  # first direction
        if ball[1] >= distance:
            ball_directions.append("<")  # second direction
        if width - ball[1] >= distance:
            ball_directions.append(">")  # third direction
        if height - ball[0] >= distance:
            ball_directions.append("v")  # third/fourth direction

    # Remove the reverse direction if it was selected
    if previous_direction and not water_just_crossed:
        if dict_reverse_direction[previous_direction] in ball_directions:
            ball_directions.remove(dict_reverse_direction[previous_direction])

    return ball_directions


def get_next_coord(ball, direction):
    """
    :param ball: current ball coordinates
    :param direction: direction that ball follows
    :param distance: distance the ball just run
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


def finalize_golf_course(golf_course):
    """
    :param golf_course: final golf course to clean
    :return: cleaned golf_course (without "BinH" and "X direction"
    """
    matrix_to_list = []
    for row in golf_course:
        for elt in row:
            if elt == "BinH":
                matrix_to_list.append(".")
            elif "X" in elt:
                if len(elt) == 1:
                    matrix_to_list.append(".")
                else:
                    matrix_to_list.append(list(elt)[1])
            else:
                matrix_to_list.append(elt)
        matrix_to_list.append('\n')

    return ''.join(matrix_to_list)


def update_golf_course(golf_course, ball, hole, distance, water_just_crossed, direction):
    # need to copy the list because of backtracking (to be able to go back to the previous state of golf course)
    golf_course_to_update = copy.deepcopy(golf_course)

    # start ball:
    golf_course_to_update[ball[0]][ball[1]] = direction
    ball = get_next_coord(ball, direction)

    for i in range(1, distance):
        if golf_course_to_update[ball[0]][ball[1]] in {".", "X"}:
            golf_course_to_update[ball[0]][ball[1]] = direction
            ball = get_next_coord(ball, direction)
        else:
            return False, None, None, None

    if golf_course_to_update[ball[0]][ball[1]] == "X":
        water_just_crossed = True
    elif golf_course_to_update[ball[0]][ball[1]] == "H" and ball != hole:
        return False, None, None, None
    elif golf_course_to_update[ball[0]][ball[1]] not in {".", "H"}:
        return False, None, None, None

    return True, water_just_crossed, golf_course_to_update, ball


def backtrack(ball, hole, distance, golf_course, water_just_crossed=False, previous_direction=None):
    # case ball is in the hole
    if ball == hole:
        golf_course[ball[0]][ball[1]] = "BinH"
        return True, golf_course, distance
    # case distance left is 0 and ball did not reach the hole
    elif distance == 0:
        return False, None, None

    # ball_direction setup (list of possible directions)
    list_directions = get_ball_directions(ball, hole, distance, golf_course, water_just_crossed, previous_direction)

    for direction in list_directions:

        is_golf_course_updated, water_just_crossed, golf_course_updated, ball_updated = \
            update_golf_course(golf_course, ball, hole, distance, water_just_crossed, direction)

        if is_golf_course_updated:
            is_backtrack_ok, golf_course_updated, distance_updated = backtrack(ball_updated, hole, distance - 1,
                                                                               golf_course_updated, water_just_crossed,
                                                                               direction)
            if is_backtrack_ok:
                return True, golf_course_updated, distance_updated
        else:
            continue

    return False, None, None


def get_path(ball, hole, dist_ball_to_hole, list_dist_ball_hole, golf_course):
    """
    :param ball: the ball coordinates (ball_row, ball_col)
    :param hole: the hole coordinates (hole_row, hole_col)
    :param dist_ball_to_hole: max distance the ball can run to reach the hole
    :param list_dist_ball_hole: the list of the "ball-to-hole" distances run so far for the current permutation
    :param golf_course: the golf course for the current permutation
    :return: if we found a "ball-to-hole" path, then we draw it on the golf course, we add the path distance to the list
             and we return True, else we return False
    """

    ball_reached_hole, golf_course, current_distance = backtrack(ball, hole, dist_ball_to_hole, golf_course)

    if ball_reached_hole:
        distance_run = sum_arithmetic_series(current_distance + 1, dist_ball_to_hole)
        list_dist_ball_hole.append(distance_run)
        return True, golf_course
    else:
        return False, None


def sum_arithmetic_series(first_term, last_term):
    """
    :param first_term: first term of the series
    :param last_term: last term of the series
    :return: sum of the arithmetic series (reason: 1)
    """
    if first_term == last_term:
        return first_term
    else:
        nb_terms = last_term - first_term + 1
        return (nb_terms * (first_term + last_term)) / 2


def calculate_distance(ball, hole):
    """
    :param ball: ball coordinates
    :param hole: hole coordinates
    :return: "ball-to-hole" distance
    """
    return abs(hole[0] - ball[0]) + abs(hole[1] - ball[1])


def is_distance_ok(list_balls, list_holes, list_dist_balls, indices):
    """
    :param list_balls: list of all the balls coordinates
    :param list_holes: list of all the holes coordinates
    :param list_dist_balls: list of all the "ball-to-hole" distances
    :param indices: list of the current permutation
    :return: True if all the balls can go to their respective hole else False
    """
    for i in range(len(list_dist_balls)):
        if sum_arithmetic_series(1, list_dist_balls[i]) < calculate_distance(list_balls[i], list_holes[indices[i]]):
            return False
    else:
        return True


def constrained_permutations(init_golf_course, list_holes, list_balls, list_dist_balls, nb_of_balls=None):
    """
    :param init_golf_course: the golf course input
    :param list_holes: the list of holes on the golf course
    :param list_balls: the list of balls to put in the holes on the golf course
    :param list_dist_balls: the list of the distances to respect for each ball
    :param nb_of_balls: the number of elements we need to permute in the list (must be equal to the number of balls)
    :return: this function yields for each possible permutation, a golf course with the "ball-to-hole" paths set and
             the sum of the distances of those paths

    permutation example:
    holes: [A, B, C]
    balls: [1, 2]
    possible hole permutations with r = 2: [A, B], [B, A], [A, C], [C, A], [B, C], [C, B]
    possible "ball-to-hole" paths: [1-A, 2-B], [1-B, 2-A], [1-A, 2-C], [1-C, 2-A], [1-B, 2-C], [1-C, 2-B]
    """
    nb_of_holes = len(list_holes)
    nb_of_permuted_elt = nb_of_holes if nb_of_balls is None else nb_of_balls
    couples_not_possible = []

    # going to iterate the indices (nb_of_holes**nb_of_permuted_elt) times:
    for indices in itertools.product(range(nb_of_holes), repeat=nb_of_permuted_elt):

        # we select nb_of_permuted_elt within nb_of_holes (order counts)
        # to do that, we select only permutations without duplicate elements
        if len(set(indices)) == nb_of_permuted_elt:

            # check that this permutation is possible ("ball-to-hole" length VS distance to be respected)
            if is_distance_ok(list_balls, list_holes, list_dist_balls, indices):

                # if (indices[i], i) couple has already been passed and is not possible
                # then we go to the next possible permutation
                for i, indices_i in enumerate(indices):
                    if (indices_i, i) in couples_not_possible:
                        break

                # for each new possible permutation, we deep-copy the golf course
                golf_course = copy.deepcopy(init_golf_course)
                list_dist_ball_hole = []
                # for each (ball, hole) couple in the permutation, we check if there is a possible path
                for i in range(nb_of_permuted_elt):
                    # because memory address of golf_course changes in the backtracking function
                    get_path_ball_to_hole, golf_course = get_path(list_balls[i], list_holes[indices[i]],
                                                                  list_dist_balls[i], list_dist_ball_hole, golf_course)
                    # if for one of the (ball, hole) couple, we don't find a "ball-to-hole" path
                    # then we go to the next possible permutation
                    if not get_path_ball_to_hole:
                        couples_not_possible.append((indices[i], i))
                        break

                # if we found a path for each of the (ball, hole) couples of this permutation:
                if len(list_dist_ball_hole) == nb_of_permuted_elt:
                    # we yield the golf course and the sum of the distances of each path
                    yield golf_course, sum(list_dist_ball_hole)


#######################################################################"
#######################################################################"
#######################################################################"

golf_course = [['.', 'X', 'X', 'X', '.', '5', 'X', '.'],
               ['X', '.', '4', '.', 'X', '.', '.', 'X'],
               ['X', '4', '.', '.', 'X', '3', '.', 'X'],
               ['X', '.', '.', '.', 'X', '.', 'X', '.'],
               ['.', 'X', '.', 'X', '.', 'H', '.', 'X'],
               ['X', '.', 'H', 'X', '.', '.', '.', 'X'],
               ['X', '.', '.', 'X', '.', 'H', '.', 'X'],
               ['.', 'X', 'H', '.', 'X', 'X', 'X', '.']]

coord_balls = [(0, 5), (1, 2), (2, 1), (2, 5)]
coord_holes = [(4, 5), (5, 2), (6, 5), (7, 2)]
dist_balls = [5, 4, 4, 3]

max_distance = len(golf_course) * len(golf_course[0])  # max distance balls can run (all the cell of the golf course)
final_golf_course = []

# we analyze each possible "ball-to-hole" path (respecting balls distance)
for golf_course_with_path, distances_ball_to_hole in constrained_permutations(golf_course, coord_holes, coord_balls,
                                                                              dist_balls, len(coord_balls)):

    # we select the golf course with the shortest paths
    if distances_ball_to_hole < max_distance:
        max_distance = distances_ball_to_hole
        final_golf_course = golf_course_with_path

# replace "BinH" by "." and "X direction" by "direction"
print(max_distance, final_golf_course)
print(finalize_golf_course(final_golf_course))
