package common.string.utils;


import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

public class StringUtilsTest {

    @Nested
    public class GetISO8601CurrentLocalTime {
        @Test
        public void test0() {
            String iso8601CurrentLocalTime = StringUtils.getISO8601CurrentLocalTime();
            assertTrue(iso8601CurrentLocalTime.contains("T"));
        }
    }

}
