package common.color;

import java.awt.Color;
import java.lang.reflect.Field;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class StringToColorConversion {
	private static final Logger LOGGER = LogManager.getLogger(StringToColorConversion.class);

	/***
	 * Source: http://www.java2s.com/Tutorial/Java/0261__2D-Graphics/Convertsagivenstringintoacolor.htm
	 * 
	 * @param inputString
	 * @return
	 */
	public static Color convertStringToColor(String inputString) {
		LOGGER.debug(() -> "Try to convert string:" + inputString + " to a color");
		if (inputString == null) {
			LOGGER.warn(() -> "Input string is null, return null");
			return null;
		}
		try {
			// get color by hex or octal value
			Color decodedColor = Color.decode(inputString);
			LOGGER.debug(() -> "Input string could be parsed hexa or octal value, return color:" + decodedColor);
			return decodedColor;
		} catch (NumberFormatException nfe) {
			// if we can't decode lets try to get it by name
			try {
				// try to get a color by name using reflection
				final Field f = Color.class.getField(inputString);
				Color color = (Color) f.get(null);
				LOGGER.debug(() -> "Input string could be parsed by name, return color:" + color);
				return color;
			} catch (Exception ce) {
				LOGGER.warn(() -> "Input string could not be parsed, return null");
				return null;
			}
		}
	}

}
