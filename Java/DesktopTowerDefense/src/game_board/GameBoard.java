package game_board;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import builders.GameBoardDataModel;
import game.Game;

public class GameBoard {

	private static final Logger LOGGER = LogManager.getLogger(GameBoard.class);

	private int total_width = 0;
	private int total_height = 0;

	private ArrayList<GameBoardPointsSeries> game_board_points_columns = new ArrayList<>();

	private GameBoardDataModel gameBoardDataModel;

	// private ArrayList<SquaresRow> squares_rows = new ArrayList<>();

	private ArrayList<GameBoardPoint> all_game_board_point_as_ordered_list = new ArrayList<GameBoardPoint>();

	private Game game;

	public GameBoard(GameBoardDataModel gameBoardDataModel) {

		this.total_width = gameBoardDataModel.getGame_board_total_width();
		this.total_height = gameBoardDataModel.getGame_board_total_height();
		this.gameBoardDataModel = gameBoardDataModel;
	}

	@SuppressWarnings("unused")
	@Deprecated
	private void create_initial_squares() {

		for (int column = 0; column < total_width; column++) {
			GameBoardPointsSeries squaresColumn = new GameBoardPointsSeries(column);
			game_board_points_columns.add(squaresColumn);
			for (int line = 0; line < total_height; line++) {
				GameBoardPointsSeries squaresRow = new GameBoardPointsSeries(line);

				// FIXME: squares_rows.add(squaresRow);

				GameBoardPoint gameBoardPoint = new GameBoardPoint(game, line, column);

				squaresColumn.addGameBoardPoint(gameBoardPoint);
				squaresRow.addGameBoardPoint(gameBoardPoint);

				all_game_board_point_as_ordered_list.add(gameBoardPoint);
			}
		}
	}

	public int getTotalWidth() {
		return total_width;
	}

	public int getTotalHeight() {
		return total_height;
	}

	public ArrayList<GameBoardPoint> getAll_squares_as_ordered_list() {
		return all_game_board_point_as_ordered_list;
	}

	public ArrayList<GameBoardPointsSeries> getSquaresColumns() {
		return game_board_points_columns;
	}

	public GameBoardPoint getSquare(int row, int column) {
		List<GameBoardPoint> square_matching_column_and_row = all_game_board_point_as_ordered_list.stream()
				.filter(item -> item.getRow() == row && item.getColumn() == column).collect(Collectors.toList());

		if (square_matching_column_and_row.size() > 1) {
			LOGGER.fatal("Found more than one (" + square_matching_column_and_row.size() + " squares with row:" + row
					+ " and column:" + column + ". FOund: " + square_matching_column_and_row);
			return null;
		}
		if (square_matching_column_and_row.isEmpty()) {
			LOGGER.error("Could not find square with row:" + row + " and column:" + column);
			return null;
		}

		return square_matching_column_and_row.get(0);
	}

	public void setGame(Game game) {
		this.game = game;
	}

	public GameBoardPoint getNeighbourSquare(GameBoardPoint reference_square, NeighbourGameBoardPointDirection direction) {
		GameBoardPoint neighbour = null;

		int reference_square_column = reference_square.getColumn();
		int reference_square_row = reference_square.getRow();

		boolean is_reference_square_first_of_column = reference_square_column == 0;
		boolean is_reference_square_last_of_column = reference_square_column == total_height - 1;

		boolean is_reference_square_first_of_row = reference_square_row == 0;
		boolean is_reference_square_last_of_row = reference_square_row == total_width - 1;

		// left square
		switch (direction) {
		case NORTH:
			if (!is_reference_square_first_of_column) {
				neighbour = getSquare(reference_square_row, reference_square_column - 1);
			}
			break;
		case NORTH_EAST:
			if (!is_reference_square_last_of_row && !is_reference_square_first_of_column) {
				neighbour = getSquare(reference_square_row + 1, reference_square_column - 1);
			}
			break;
		case EAST:
			if (!is_reference_square_last_of_row) {
				neighbour = getSquare(reference_square_row + 1, reference_square_column);
			}
			break;
		case SOUTH_EAST:
			if (!is_reference_square_last_of_row && !is_reference_square_last_of_column) {
				neighbour = getSquare(reference_square_row + 1, reference_square_column + 1);
			}
			break;
		case SOUTH:
			if (!is_reference_square_last_of_column) {
				neighbour = getSquare(reference_square_row, reference_square_column + 1);
			}
			break;
		case SOUTH_WEST:
			if (!is_reference_square_first_of_row && !is_reference_square_last_of_column) {
				neighbour = getSquare(reference_square_row - 1, reference_square_column + 1);
			}
			break;
		case WEST:
			if (!is_reference_square_first_of_row) {
				neighbour = getSquare(reference_square_row - 1, reference_square_column);
			}
			break;
		case NORTH_WEST:
			if (!is_reference_square_first_of_row && !is_reference_square_first_of_column) {
				neighbour = getSquare(reference_square_row - 1, reference_square_column - 1);
			}
			break;
		}
		return neighbour;
	}

	public GameBoardDataModel getGameBoardDataModel() {
		return gameBoardDataModel;
	}
}