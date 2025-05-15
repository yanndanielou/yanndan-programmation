package common.arrays;


import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

public class ArrayUtilsTest {

    @Test
    void nullArgument() {
        assertNull(ArrayUtils.byteArrayToIntArray(null));
    }

    @Test
    void validTable() {
        int[] intArray = {1, 2, 3};
        byte[] byteArray = {1, 2, 3};
        assertArrayEquals(intArray, ArrayUtils.byteArrayToIntArray(byteArray));
    }

}
