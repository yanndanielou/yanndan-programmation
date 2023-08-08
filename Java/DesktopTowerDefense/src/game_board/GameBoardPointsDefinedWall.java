package game_board;

import java.awt.Rectangle;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import builders.game_board.RectangleDataModel;
import game.Game;

public class GameBoardPointsDefinedWall extends GameBoardRectangleDefinedArea {

	/**
	 * 
	 */
	private static final long serialVersionUID = 8239100426793054601L;
	@SuppressWarnings("unused")
	private static final Logger LOGGER = LogManager.getLogger(GameBoardPointsDefinedWall.class);

	@Deprecated
	public GameBoardPointsDefinedWall(Game game, Rectangle rectangle, String name) {
		super(game, rectangle, name);
	}

	public GameBoardPointsDefinedWall(Game game, RectangleDataModel rectangleDataModel) {
		super(game, rectangleDataModel);
	}

}