package builders.game_board;

import java.awt.Color;

public class GameBoardAreasByRGBImageRecognitionDataModel {

	private String name;
	private String imageToParsePath;

	private ColorDefinition rgbColorDefinition;

	class ColorDefinition {
		int red;
		int green;
		int blue;
	}

	public String getName() {
		return name;
	}

	public String getImageToParsePath() {
		return imageToParsePath;
	}

	public Color getBackgroundColorAsAwtColor() {
		Color color = null;
		if (rgbColorDefinition != null) {
			color = new Color(rgbColorDefinition.red, rgbColorDefinition.green, rgbColorDefinition.blue);
		}
		return color;
	}

}