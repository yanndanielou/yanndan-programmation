package common.color;

import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.awt.*;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

public class StringToColorConversionTest {

    @Nested
    public class ConvertStringToColor {
        @Nested
        public class BadUsages {
            @Test
            void nullArgument() {
                assertNull(StringToColorConversion.convertStringToColor(null));
            }

            @Test
            void invalidColorName() {
                assertNull(StringToColorConversion.convertStringToColor("not existing color"));
            }
        }

        @Nested
        public class CorrectUsages {
            private static Stream<Arguments> provideColorsByName() {

                // @formatter:off
				return Stream.of(
						Arguments.of(Color.blue, "blue"),
						Arguments.of(Color.black, "black"),
						Arguments.of(Color.red, "red"),
						Arguments.of(Color.YELLOW, "YELLOW"),
						Arguments.of(Color.yellow, "yellow")
						);
				// @formatter:on	
            }

            @ParameterizedTest
            @MethodSource("provideColorsByName")
            void colorName(Color colorAsColor, String colorAsString) {
                assertEquals(colorAsColor, StringToColorConversion.convertStringToColor(colorAsString));
            }

            @Test
            void byRBG() {
                assertEquals(Color.gray, StringToColorConversion.convertStringToColor("" + Color.gray.getRGB()));
            }
        }
    }

}
