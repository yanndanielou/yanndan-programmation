package game_board;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import geometry.IntegerRectangle;

public class GameBoardPredefinedConstructionLocation extends GameBoardArea {

	@SuppressWarnings("unused")
	private static final Logger LOGGER = LogManager.getLogger(GameBoardPredefinedConstructionLocation.class);

	public GameBoardPredefinedConstructionLocation(GameBoard gameBoard, IntegerRectangle rectangleInImageWithRGB) {
		super(gameBoard, rectangleInImageWithRGB, "");
	}

	public boolean isNewConstructionAllowed() {
		for (GameBoardPoint gameBoardPoint : getAllPoints()) {
			if (gameBoardPoint.isWall() || gameBoardPoint.isOccupiedByTower() || gameBoardPoint.isNonPlayableArea()
					|| gameBoardPoint.isOccupiedByAttacker()) {
				return false;
			}
		}
		return true;
	}

}