/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package cfx00854407.network;

/**
 *
 * @author z003urxb
 */
public class Response implements AFFCARMessage{
    
    public static final int MSG_SIZE = 13;
    
    private int AFFCAR_ID = (int)0x0000;
    private int Sw_Version_Major = (int)0x00;
    private int Sw_Version_Minor = (int)0x00;
    private byte Health = (byte)0xff;
    private int DAM_1 = 0;
    private int DAM_0 = 0;

    public Response() {
    }

    @Override
    public byte[] getBytes() throws PacketFormatException {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public void putBytes(byte[] bytes) {
        if(bytes.length>=MSG_SIZE){
            AFFCAR_ID = (int)((0xff & bytes[0])<<8 | (0xff & bytes[1]));
            Sw_Version_Major = bytes[2];
            Sw_Version_Minor = bytes[3];
            Health = bytes[4];
            DAM_1 = (0xff & bytes[5])<<24 | (0xff & bytes[6])<<16 | (0xff & bytes[7])<<8 | (0xff & bytes[8]);
            DAM_0 = (0xff & bytes[9])<<24 | (0xff & bytes[10])<<16 | (0xff & bytes[11])<<8 | (0xff & bytes[12]);
        }
    }

    public int getAFFCAR_ID() {
        return AFFCAR_ID;
    }
    
    public int getSwVersionMajor() {
        return Sw_Version_Major;
    }
    
    public int getSwVersionMinor() {
        return Sw_Version_Minor;
    }

    public byte getHealth() {
        return Health;
    }

    public int getDAM_1() {
        return DAM_1;
    }

    public int getDAM_0() {
        return DAM_0;
    }
    
    
    
}
