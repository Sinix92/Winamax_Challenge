# A ball with a shotcount N will jump by N cells in one direction, vertically or horizontally.
# The shotcount is then decreased by 1 and the ball can jump again.

import itertools
import copy


def get_ball_directions(ball, hole, golf_course, previous_direction=None):
    """
    :param ball: current ball coordinates
    :param hole: hole coordinates that ball targets
    :param golf_course: current state of golf course
    :param previous_direction: direction that ball just followed
    :return: list of possible directions that ball will follow (avoid reverse direction)
    """
    height = len(golf_course)
    width = len(golf_course[0])

    dict_reverse_direction = {"v": "^", "^": "v", "<": ">", ">": "<"}
    ball_directions = []

    ############## ball to the top left of the hole ##############
    if ball[0] < hole[0] and ball[1] < hole[1]:
        ball_directions.append("v")  # first direction
        ball_directions.append(">")  # second direction
        if ball[1] > 0:
            ball_directions.append("<")  # third direction
        if ball[0] > 0:
            ball_directions.append("^")  # third/fourth direction

    ############## ball right above the hole ##############
    elif ball[0] < hole[0] and ball[1] == hole[1]:
        ball_directions.append("v")  # first direction
        if ball[1] > 0:
            ball_directions.append("<")  # second direction
        if ball[1] < width - 1:
            ball_directions.append(">")  # second/third direction
        if ball[0] > 0:
            ball_directions.append("^")  # second/third/fourth direction

    ############## ball to the top right of the hole ##############
    elif ball[0] < hole[0] and ball[1] > hole[1]:
        ball_directions.append("v")  # first direction
        ball_directions.append("<")  # second direction
        if ball[1] < width - 1:
            ball_directions.append(">")  # third direction
        if ball[0] > 0:
            ball_directions.append("^")  # third/fourth direction

    ############## ball to the left of the hole ##############
    elif ball[0] == hole[0] and ball[1] < hole[1]:
        ball_directions.append(">")  # first direction
        if ball[0] > 0:
            ball_directions.append("^")  # second direction
        if ball[0] < height - 1:
            ball_directions.append("v")  # second/third direction
        if ball[1] > 0:
            ball_directions.append("<")  # second/third/fourth direction

    ############## ball to the right of the hole ##############
    elif ball[0] == hole[0] and ball[1] > hole[1]:
        ball_directions.append("<")  # first direction
        if ball[0] > 0:
            ball_directions.append("^")  # second direction
        if ball[0] < height - 1:
            ball_directions.append("v")  # second/third direction
        if ball[1] < width - 1:
            ball_directions.append(">")  # second/third/fourth direction

    ############## ball to the down left of the hole ##############
    elif ball[0] > hole[0] and ball[1] < hole[1]:
        ball_directions.append("^")  # first direction
        ball_directions.append(">")  # second direction
        if ball[1] > 0:
            ball_directions.append("<")  # third direction
        if ball[0] < height - 1:
            ball_directions.append("v")  # third/fourth direction

    ############## ball right below the hole ##############
    elif ball[0] > hole[0] and ball[1] == hole[1]:
        ball_directions.append("^")  # first direction
        if ball[1] > 0:
            ball_directions.append("<")  # second direction
        if ball[1] < width - 1:
            ball_directions.append(">")  # second/third direction
        if ball[0] < height - 1:
            ball_directions.append("v")  # second/third/fourth direction

    ############## ball to the down right of the hole ##############
    elif ball[0] > hole[0] and ball[1] > hole[1]:
        ball_directions.append("^")  # first direction
        ball_directions.append("<")  # second direction
        if ball[1] < width - 1:
            ball_directions.append(">")  # third direction
        if ball[0] < height - 1:
            ball_directions.append("v")  # third/fourth direction

    if previous_direction:
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


def backtrack(init_ball, current_ball, hole, dist_ball_to_hole, golf_course, current_distance, previous_direction=None):
    """
    :param init_ball: starting ball coordinates
    :param current_ball: current ball coordinates
    :param hole: hole coordinate that ball targets
    :param dist_ball_to_hole: "ball-to-hole" distance to be respected
    :param golf_course: current state of golf course
    :param current_distance: current "ball-to-hole" distance
    :param previous_direction: previous direction ball just followed
    :return: a boolean saying if ball got to the hole, current state of golf course, current "ball-to-hole" distance
    """

    # if current "ball-to-hole" distance is above or equal to the one to respect
    if current_distance > dist_ball_to_hole:
        return False, None, current_distance - 1  # subtract 1 from current_distance because we backtrack to previous state

    # if ball is out of golf course (only possible after having passed an "X")
    if current_ball[0] >= len(golf_course) or current_ball[1] >= len(golf_course[0]):
        return False, None, current_distance  # don't subtract 1 from current_distance because we just passed an "X"

    # if the ball meets the hole
    if current_ball == hole:
        current_distance += 1
        golf_course[current_ball[0]][current_ball[1]] = "BinH"
        return True, golf_course, current_distance

    # ball_direction setup (list of possible directions)
    list_ball_directions = get_ball_directions(current_ball, hole, golf_course, previous_direction)

    # need to copy the list because of backtracking (to be able to go back to the previous state of golf course)
    updated_golf_course = copy.deepcopy(golf_course)

    x_already_met = False  # boolean in case we met an "X" in the previous failing backtrack
    for direction in list_ball_directions:

        # if current ball coordinates are the ones of starting ball
        if current_ball == init_ball:
            updated_golf_course[current_ball[0]][current_ball[1]] = direction
        # when the ball meets a "."
        elif updated_golf_course[current_ball[0]][current_ball[1]] == ".":
            current_distance += 1
            updated_golf_course[current_ball[0]][current_ball[1]] = direction
        # when the ball meets an "X"
        elif updated_golf_course[current_ball[0]][current_ball[1]] == "X":
            if x_already_met:
                return False, None, current_distance  # don't subtract 1 from current_distance because we just passed an "X"
            direction = previous_direction
            updated_golf_course[current_ball[0]][current_ball[1]] = "X{}".format(direction)
        # when the ball meets anything else than ".", or "H"
        else:
            return False, None, current_distance  # no need subtract 1 from current_distance because we didn't add 1

        # get the next coordinates of the ball
        next_ball = get_next_coord(current_ball, direction)

        # recursion until the ball gets to the hole
        backtrack_boolean, updated_golf_course, current_distance = backtrack(init_ball, next_ball, hole,
                                                                             dist_ball_to_hole, updated_golf_course,
                                                                             current_distance, direction)
        # check if the ball got to the hole
        if backtrack_boolean:
            return True, updated_golf_course, current_distance
        else:
            # if we got a fail coming out from the last backtracking
            # reload previous golf_course
            updated_golf_course = copy.deepcopy(golf_course)
            x_already_met = True

    else:
        # if regardless the direction, it is not possible to find a path
        if "X" not in updated_golf_course[current_ball[0]][current_ball[1]] and current_distance != 0:
            current_distance -= 1
        return False, None, current_distance


def get_path(ball, hole, dist_ball_to_hole, list_dist_ball_hole, golf_course):
    """
    :param ball: the ball coordinates (ball_row, ball_col)
    :param hole: the hole coordinates (hole_row, hole_col)
    :param dist_ball_to_hole: max distance the ball can run to reach the hole
    :param list_dist_ball_hole: the list of the "ball-to-hole" distances for the current permutation
    :param golf_course: the golf course for the current permutation
    :return: if we found a "ball-to-hole" path, then we draw it on the golf course, we add the path distance to the list
             and we return true, else we return false
    """

    # "ball-to-hole" run distance at the beginning of the path
    current_distance = 0

    ball_reached_hole, golf_course, current_distance = backtrack(ball, ball, hole, dist_ball_to_hole, golf_course,
                                                                 current_distance)
    if ball_reached_hole:
        list_dist_ball_hole.append(current_distance)
        return True, golf_course
    else:
        return False, None


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
    holes = tuple(list_holes)
    balls = tuple(list_balls)
    dist_balls_holes = tuple(list_dist_balls)
    nb_of_holes = len(holes)
    nb_of_permuted_elt = nb_of_holes if nb_of_balls is None else nb_of_balls

    # going to iterate the indices (nb_of_holes**nb_of_permuted_elt) times:
    for indices in itertools.product(range(nb_of_holes), repeat=nb_of_permuted_elt):

        # we select nb_of_permuted_elt within nb_of_holes (order counts)
        # to do that, we select only permutations without duplicate elements
        if len(set(indices)) == nb_of_permuted_elt:
            # for each new possible permutation, we deep-copy the golf course
            golf_course = copy.deepcopy(init_golf_course)
            list_dist_ball_hole = []
            # for each (ball, hole) couple in the permutation, we check if there is a possible path
            for i in range(nb_of_permuted_elt):
                # because memory address of golf_course changes in the backtracking function
                get_path_ball_to_hole, golf_course = get_path(balls[i], holes[indices[i]], dist_balls_holes[i],
                                                              list_dist_ball_hole, golf_course)
                # if for one of the (ball, hole) couple, we don't find a "ball-to-hole" path
                # then we go to the next possible permutation
                if not get_path_ball_to_hole:
                    break

            # if we found a path for each of the (ball, hole) couples of this permutation:
            if len(list_dist_ball_hole) == nb_of_permuted_elt:
                # we yield the golf course and the sum of the distances of each path
                yield golf_course, sum(list_dist_ball_hole)


#######################################################################"
#######################################################################"
#######################################################################"

golf_course = [['4', '.', '.', 'X', 'X'],
               ['.', 'H', '.', 'H', '.'],
               ['.', '.', '.', 'H', '.'],
               ['.', '2', '.', '.', '2'],
               ['.', '.', '.', '.', '.']]

coord_balls = [(0, 0), (3, 1), (3, 4)]
coord_holes = [(1, 1), (1, 3), (2, 3)]
dist_balls = [4, 2, 2]

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
print(final_golf_course)
print(finalize_golf_course(final_golf_course))
