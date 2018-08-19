from cProfile import run as cProfile_run
from copy import deepcopy as copy_deepcopy


def finalize_golf_course(golf_course):
    """
    :param golf_course: final golf course to clean
    :return: cleaned golf_course (without "BinH" and "X direction"
    """
    matrix_to_list = []
    for row in golf_course:
        for elt in row:
            if elt == "BinH":
                matrix_to_list.append("H")
            elif "X" in elt:
                if len(elt) == 1:
                    matrix_to_list.append(".")
                else:
                    matrix_to_list.append(list(elt)[1])
            else:
                matrix_to_list.append(elt)
        matrix_to_list.append('\n')

    return ''.join(matrix_to_list)


def get_ball_directions(golf_course, ball, distance, water_just_crossed, previous_direction):
    dict_reverse_direction = {"v": "^", "^": "v", "<": ">", ">": "<"}
    ball_directions = []

    height = len(golf_course) - 1
    width = len(golf_course[0]) - 1

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
        if ball[0] >= distance:
            ball_directions.append("^")  # first direction
        if width - ball[1] >= distance:
            ball_directions.append(">")  # third direction
        if height - ball[0] >= distance:
            ball_directions.append("v")  # second direction
        if ball[1] >= distance:
            ball_directions.append("<")  # fourth direction

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
    water_just_crossed = False
    # need to copy the list because of backtracking (to be able to go back to the previous state of golf course)
    golf_course_to_update = copy_deepcopy(golf_course)

    # start ball:
    golf_course_to_update[ball[0]][ball[1]] = direction
    ball = get_next_coord((ball[0], ball[1]), direction)

    for i in range(1, distance):
        if golf_course_to_update[ball[0]][ball[1]] in {".", "X"}:
            golf_course_to_update[ball[0]][ball[1]] = direction
            ball = get_next_coord(ball, direction)
        else:
            return False, None, None, None, None

    if golf_course_to_update[ball[0]][ball[1]] == "X":
        water_just_crossed = True
    elif golf_course_to_update[ball[0]][ball[1]] == "BinH":
        return False, None, None, None, (ball[0], ball[1])
    elif golf_course_to_update[ball[0]][ball[1]] not in {".", "H"}:
        return False, None, None, None, None

    return True, water_just_crossed, golf_course_to_update, ball, None


def backtrack(golf_course, start_ball, ball, distance, holes_double_targeted, couples_to_avoid,
              water_just_crossed=False,
              previous_direction=None):
    # case ball is in the hole
    if golf_course[ball[0]][ball[1]] == "H":
        if start_ball in couples_to_avoid:
            if ball in couples_to_avoid[start_ball]:
                return False, None, None
        golf_course[ball[0]][ball[1]] = "BinH"
        return True, golf_course, (ball[0], ball[1])
    # case distance left is 0 and ball did not reach the hole
    elif distance == 0:
        return False, None, None

    # ball_direction setup (list of possible directions)
    list_directions = get_ball_directions(golf_course, ball, distance, water_just_crossed, previous_direction)

    print(finalize_golf_course(golf_course))

    for direction in list_directions:

        is_golf_course_updated, water_just_crossed, golf_course_updated, ball_updated, hole_BinH = \
            update_golf_course(golf_course, ball, distance, direction)

        if is_golf_course_updated:
            is_backtrack_ok, golf_course_updated, hole = backtrack(golf_course_updated, start_ball, ball_updated,
                                                                   distance - 1, holes_double_targeted,
                                                                   couples_to_avoid, water_just_crossed, direction)
            if is_backtrack_ok:
                return True, golf_course_updated, hole
        else:
            if hole_BinH:
                holes_double_targeted.add(hole_BinH)
            continue

    return False, None, None


def get_possible_paths(golf_course, balls, distances, couples_to_avoid={}, last_hole_input=None):
    while True:
        golf_course_updated = golf_course
        hole_ball_couples = {}
        holes_double_targeted = set()
        # Loop through the balls
        for index, ball in enumerate(balls):
            is_backtrack_ok, golf_course_updated, hole = backtrack(golf_course_updated, ball, ball, distances[index],
                                                                   holes_double_targeted, couples_to_avoid)

            print(finalize_golf_course(golf_course_updated))
            print("=========================================")

            if not is_backtrack_ok:
                if holes_double_targeted:
                    for hole in holes_double_targeted:
                        if hole in hole_ball_couples:
                            if hole_ball_couples[hole] not in couples_to_avoid:
                                couples_to_avoid[hole_ball_couples[hole]] = set(hole)
                            else:
                                couples_to_avoid[hole_ball_couples[hole]].add(hole)

                            golf_course_updated, hole_ball_couples = get_possible_paths(golf_course, balls, distances,
                                                                                        couples_to_avoid, hole)
                            if len(balls) == len(hole_ball_couples):
                                return golf_course_updated, hole_ball_couples

                else:
                    if last_hole_input:
                        if ball in couples_to_avoid:
                            if last_hole_input in couples_to_avoid[ball]:
                                couples_to_avoid[ball].remove(last_hole_input)
                    break
            else:
                hole_ball_couples[hole] = ball

        if len(balls) == len(hole_ball_couples):
            break

    return golf_course_updated, hole_ball_couples


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

    balls = [(2, 29), (2, 39), (2, 40), (3, 3), (3, 16), (3, 23), (3, 33), (3, 46), (6, 6), (6, 13), (6, 26),
             (6, 36), (6, 43), (7, 0), (7, 19), (7, 20), (7, 30)]
    # holes = [(0, 23), (0, 33), (0, 46), (3, 2), (3, 17), (3, 22), (3, 32), (9, 4), (9, 6), (9, 13), (9, 15),
    #                (9, 24), (9, 26), (9, 34), (9, 36), (9, 43), (9, 45)]
    distances = [4, 4, 4, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3]

    ####### Calculate the number of possible paths #######
    nb_possibilities = 0
    for distance in distances:
        nb_possibilities += 4 * (1 if distance == 1 else 3 ** (distance - 1))
    print("Number of possibilities: {}".format(nb_possibilities))
    ######################################################

    # we get the final golf course
    final_golf_course, hole_ball_couples = get_possible_paths(golf_course, balls, distances)

    # replace "BinH" by "." and "X direction" by "direction"
    print(final_golf_course)
    # print(finalize_golf_course(final_golf_course))


if __name__ == "__main__":
    cProfile_run('main()')
    # main()
