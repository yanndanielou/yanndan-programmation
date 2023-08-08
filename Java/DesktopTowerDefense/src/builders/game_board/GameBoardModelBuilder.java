package builders.game_board;

import java.awt.Color;
import java.awt.Point;
import java.awt.image.BufferedImage;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import javax.imageio.ImageIO;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import com.google.gson.Gson;

import game.Game;
import game_board.GameBoard;
import game_board.GameBoardAttackersEntryArea;
import game_board.GameBoardAttackersExitArea;
import game_board.GameBoardRectangleDefinedWall;
import geometry.IntegerRectangle;

public class GameBoardModelBuilder {
	private static final Logger LOGGER = LogManager.getLogger(GameBoardModelBuilder.class);

	private Gson gson = new Gson();

	private GameBoardDataModel gameBoardDataModel;

	public GameBoardDataModel getGameBoardDataModel() {
		return gameBoardDataModel;
	}

	public GameBoardModelBuilder(String game_board_data_model_json_file) {
		BufferedReader br = null;

		try {

			br = new BufferedReader(new FileReader(game_board_data_model_json_file));

		} catch (IOException e) {
			e.printStackTrace();
		}
		gameBoardDataModel = gson.fromJson(br, GameBoardDataModel.class);
	}

	public void buildAllAreas(Game game, GameBoard gameBoard) {

		for (RectangleDataModel wallDataModel : gameBoardDataModel.getWallsAsRectangles()) {
			GameBoardRectangleDefinedWall wall = new GameBoardRectangleDefinedWall(game, wallDataModel);
			gameBoard.addWall(wall);
		}
		for (GameBoardAreasByRGBImageRecognitionDataModel wallDataModel : gameBoardDataModel
				.getPointsDefinedWallAreaAsRGBInImageToParse()) {
		}
		for (RectangleDataModel attackersEntryAreaDataModel : gameBoardDataModel.getAttackersEntryAreasAsRectangles()) {
			GameBoardAttackersEntryArea attackersEntryArea = new GameBoardAttackersEntryArea(game,
					attackersEntryAreaDataModel);
			gameBoard.addGameBoardAttackersEntryArea(attackersEntryArea);
		}
		for (RectangleDataModel attackersExitAreaDataModel : gameBoardDataModel.getAttackersExitAreasAsRectangles()) {
			GameBoardAttackersExitArea attackersExitArea = new GameBoardAttackersExitArea(game,
					attackersExitAreaDataModel);
			gameBoard.addGameBoardAttackersExitArea(attackersExitArea);
		}
	}

	private List<Point> getListOfPixelsInImageWithRGB(
			GameBoardAreasByRGBImageRecognitionDataModel gameBoardAreasByRGBImageRecognitionDataModel) {

		Color searchedColor = gameBoardAreasByRGBImageRecognitionDataModel.getBackgroundColorAsAwtColor();

		List<Point> pointsInImageWithRGB = new ArrayList<>();

		File imageFile = new File(gameBoardAreasByRGBImageRecognitionDataModel.getImageToParsePath());
		BufferedImage imageBufferedImage = null;
		try {
			imageBufferedImage = ImageIO.read(imageFile);
		} catch (IOException e) {
			e.printStackTrace();
		}

		int imageWidth = imageBufferedImage.getWidth();
		int imageHeight = imageBufferedImage.getHeight();

		for (int x = 0; x < imageWidth; x++) {

			for (int y = 0; y < imageHeight; y++) {
				int pixel_rgb = -1;
				try {
					pixel_rgb = imageBufferedImage.getRGB(x, y);

				} catch (ArrayIndexOutOfBoundsException e) {
					LOGGER.fatal("x:" + x + ", y:" + y + ", " + e.getLocalizedMessage());
					// e.printStackTrace();
					continue;
				}

				int blue = pixel_rgb & 0xff;
				int green = (pixel_rgb & 0xff00) >> 8;
				int red = (pixel_rgb & 0xff0000) >> 16;

				Color pixelColor = new Color(pixel_rgb);
				int red2 = pixelColor.getRed();
				int blue2 = pixelColor.getBlue();
				int green2 = pixelColor.getGreen();

				if (searchedColor.equals(pixelColor)) {
					pointsInImageWithRGB.add(new Point(x, y));
				}
			}
		}

		return null;
	}

	private IntegerRectangle getRectangleInImageWithRGB(
			GameBoardAreasByRGBImageRecognitionDataModel gameBoardAreasByRGBImageRecognitionDataModel) {

		return null;
	}

}